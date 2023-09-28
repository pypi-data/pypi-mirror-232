"""Masked autoregressive network and bijection."""

from functools import partial
from typing import Callable

import equinox as eqx
import jax
import jax.nn as jnn
import jax.numpy as jnp
from jax import Array
from jax.random import KeyArray

from flowjax.bijections.bijection import Bijection
from flowjax.bijections.jax_transforms import Batch
from flowjax.nn import AutoregressiveMLP
from flowjax.utils import get_ravelled_bijection_constructor


class MaskedAutoregressive(Bijection):
    """Masked autoregressive bijection implementation (https://arxiv.org/abs/1705.07057v4).
    The transformer is parameterised by a neural network, with weights masked to ensure
    an autoregressive structure.
    """

    transformer_constructor: Callable
    autoregressive_mlp: AutoregressiveMLP

    def __init__(
        self,
        key: KeyArray,
        transformer: Bijection,
        dim: int,
        cond_dim: int | None,
        nn_width: int,
        nn_depth: int,
        nn_activation: Callable = jnn.relu,
    ) -> None:
        """
        Args:
            key (KeyArray): Jax PRNGKey
            transformer (Bijection): Bijection with shape () to be parameterised by the
                autoregressive network.
            dim (int): Dimension.
            cond_dim (int | None): Dimension of any conditioning variables.
            nn_width (int): Neural network width.
            nn_depth (int): Neural network depth.
            nn_activation (Callable): Neural network activation. Defaults to jnn.relu.
        """
        if transformer.shape != () or transformer.cond_shape is not None:
            raise ValueError(
                "Only unconditional transformers with shape () are supported."
            )

        constructor, transformer_init_params = get_ravelled_bijection_constructor(
            transformer
        )

        if cond_dim is None:
            self.cond_shape = None
            in_ranks = jnp.arange(dim)
        else:
            self.cond_shape = (cond_dim,)
            # we give conditioning variables rank -1 (no masking of edges to output)
            in_ranks = jnp.hstack((jnp.arange(dim), -jnp.ones(cond_dim)))

        hidden_ranks = jnp.arange(nn_width) % dim
        out_ranks = jnp.repeat(jnp.arange(dim), transformer_init_params.size)

        autoregressive_mlp = AutoregressiveMLP(
            in_ranks,
            hidden_ranks,
            out_ranks,
            nn_depth,
            nn_activation,
            key=key,
        )

        # Initialise bias terms to match the provided transformer parameters
        self.autoregressive_mlp = eqx.tree_at(
            where=lambda t: t.layers[-1].linear.bias,  # type: ignore
            pytree=autoregressive_mlp,
            replace=jnp.tile(transformer_init_params, dim),
        )

        self.transformer_constructor = constructor
        self.shape = (dim,)
        self.cond_shape = None if cond_dim is None else (cond_dim,)

    def transform(self, x, condition=None):
        nn_input = x if condition is None else jnp.hstack((x, condition))
        transformer_params = self.autoregressive_mlp(nn_input)
        transformer = self._flat_params_to_transformer(transformer_params)
        return transformer.transform(x)

    def transform_and_log_det(self, x, condition=None):
        nn_input = x if condition is None else jnp.hstack((x, condition))
        transformer_params = self.autoregressive_mlp(nn_input)
        transformer = self._flat_params_to_transformer(transformer_params)
        return transformer.transform_and_log_det(x)

    def inverse(self, y, condition=None):
        init = (y, 0)
        fn = partial(self.inv_scan_fn, condition=condition)
        (x, _), _ = jax.lax.scan(fn, init, None, length=len(y))
        return x

    def inv_scan_fn(self, init, _, condition):
        """One 'step' in computing the inverse."""
        y, rank = init
        nn_input = y if condition is None else jnp.hstack((y, condition))
        transformer_params = self.autoregressive_mlp(nn_input)
        transformer = self._flat_params_to_transformer(transformer_params)
        x = transformer.inverse(y)
        x = y.at[rank].set(x[rank])
        return (x, rank + 1), None

    def inverse_and_log_det(self, y, condition=None):
        x = self.inverse(y, condition)
        log_det = self.transform_and_log_det(x, condition)[1]
        return x, -log_det

    def _flat_params_to_transformer(self, params: Array):
        """Reshape to dim X params_per_dim, then vmap."""
        dim = self.shape[-1]  # type: ignore
        transformer_params = jnp.reshape(params, (dim, -1))
        transformer = eqx.filter_vmap(self.transformer_constructor)(transformer_params)
        return Batch(transformer, (dim,), vectorize_bijection=True)
