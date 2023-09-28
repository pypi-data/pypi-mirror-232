"""Planar transform, i.e. a layer in a planar flow introduced in
https://arxiv.org/pdf/1505.05770.pdf.
"""

import equinox as eqx
import jax.numpy as jnp
import jax.random as jr
from jax import Array
from jax.nn import softplus
from jax.numpy.linalg import norm

from flowjax.bijections import Bijection


class Planar(Bijection):
    r"""Planar bijection as used by https://arxiv.org/pdf/1505.05770.pdf. Uses the
    transformation :math:`y + u \cdot \text{tanh}(w \cdot x + b)`, where
    :math:`u \in \mathbb{R}^D, \ w \in \mathbb{R}^D` and :math:`b \in \mathbb{R}`. In
    the unconditional case, :math:`w`, :math:`u`  and :math:`b` are learned directly.
    In the conditional case they are parameterised by an MLP.
    """

    conditioner: eqx.Module | None
    params: Array | None

    def __init__(
        self,
        key: jr.KeyArray,
        dim: int,
        cond_dim: int | None = None,
        **mlp_kwargs,
    ):
        """
        Args:
            key (jr.KeyArray): Jax random seed.
            dim (int): Dimension of the bijection.
            cond_dim (int | None, optional): Dimension of extra conditioning variables.
                Defaults to None.
            **mlp_kwargs: Key word arguments passed to the MLP conditioner. Ignored
                when cond_dim is None.
        """
        self.shape = (dim,)

        if cond_dim is None:
            self.params = 0.01 * jr.normal(key, (2 * dim + 1,))
            self.conditioner = None
            self.cond_shape = None
        else:
            self.params = None
            self.conditioner = eqx.nn.MLP(dim, 2 * dim + 1, **mlp_kwargs, key=key)
            self.cond_shape = (cond_dim,)

    def transform(self, x, condition=None):
        x, condition = self._argcheck_and_cast(x, condition)
        return self.get_planar(condition).transform(x)

    def transform_and_log_det(self, x, condition=None):
        x, condition = self._argcheck_and_cast(x, condition)
        return self.get_planar(condition).transform_and_log_det(x)

    def inverse(self, y, condition=None):
        return self.get_planar(condition).inverse(y)

    def inverse_and_log_det(self, y, condition=None):
        return self.get_planar(condition).inverse_and_log_det(y)

    def get_planar(self, condition=None):
        "Get the planar bijection with the conditioning applied if conditional."
        if self.cond_shape is not None:
            params = self.conditioner(condition)
        else:
            params = self.params
        dim = self.shape[0]
        w, u, bias = params[:dim], params[dim : 2 * dim], params[-1]
        return _UnconditionalPlanar(w, u, bias)


class _UnconditionalPlanar(Bijection):
    """Unconditional planar bijection, used in Planar."""

    weight: Array
    _act_scale: Array
    bias: Array

    def __init__(self, weight, act_scale, bias):
        """Construct an unconditional planar bijection. Note act_scale (u in the paper)
        is unconstrained and the constraint to ensure invertiblitiy is applied in the
        ``get_act_scale``."""
        self.weight = weight
        self._act_scale = act_scale
        self.bias = bias
        self.shape = weight.shape
        self.cond_shape = None

    def transform(self, x, condition=None):
        return x + self.get_act_scale() * jnp.tanh(self.weight @ x + self.bias)

    def transform_and_log_det(self, x, condition=None):
        u = self.get_act_scale()
        act = jnp.tanh(x @ self.weight + self.bias)
        y = x + u * act
        psi = (1 - act**2) * self.weight
        log_det = jnp.log(jnp.abs(1 + u @ psi))
        return y, log_det

    def get_act_scale(self):
        """Apply constraint to u to ensure invertibility. See appendix A1 in
        https://arxiv.org/pdf/1505.05770.pdf."""
        wtu = self._act_scale @ self.weight
        m_wtu = -1 + jnp.log(1 + softplus(wtu))
        u = self._act_scale + (m_wtu - wtu) * self.weight / norm(self.weight) ** 2
        return u

    def inverse(self, y, condition=None):
        raise NotImplementedError(
            "The inverse planar transformation is not implemented."
        )

    def inverse_and_log_det(self, y, condition=None):
        raise NotImplementedError(
            "The inverse planar transformation is not implemented."
        )
