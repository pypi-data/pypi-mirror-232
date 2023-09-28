<div align="center">
<img src="./logo.png?raw=true" alt="logo" width="500" ></img>
</div>

# FlowJax: Normalizing Flows in Jax

## Documentation
Available [here](https://danielward27.github.io/flowjax/index.html).

## Short example
Training a flow can be done in a few lines of code:

```
from flowjax.flows import BlockNeuralAutoregressiveFlow
from flowjax.train import fit_to_data
from flowjax.distributions import Normal
from jax import random
import jax.numpy as jnp

data_key, flow_key, train_key = random.split(random.PRNGKey(0), 3)

x = random.uniform(data_key, (10000, 3))  # Toy data
base_dist = Normal(jnp.zeros(x.shape[1]))
flow = BlockNeuralAutoregressiveFlow(flow_key, base_dist)
flow, losses = fit_to_data(train_key, flow, x, learning_rate=1e-2)

# We can now evaluate the log-probability of arbitrary points
flow.log_prob(x)
```

The package currently includes:
- Many simple bijections and distributions, implemented as [Equinox](https://arxiv.org/abs/2111.00254) modules.
- `CouplingFlow` ([Dinh et al., 2017](https://arxiv.org/abs/1605.08803)) and `MaskedAutoregressiveFlow` ([Kingma et al., 2016](https://arxiv.org/abs/1606.04934), [Papamakarios et al., 2017](https://arxiv.org/abs/1705.07057v4)) normalizing flow architectures.
    - These can be used with arbitrary bijections as transformers, such as `Affine` or `RationalQuadraticSpline` (the latter used in neural spline flows; [Durkan et al., 2019](https://arxiv.org/abs/1906.04032)). 
- `BlockNeuralAutoregressiveFlow`, as introduced by [De Cao et al., 2019](https://arxiv.org/abs/1904.04676)
- `PlanarFlow`, as introduced by [Rezende and Mohamed, 2015](https://arxiv.org/pdf/1505.05770.pdf).
- `TriangularSplineFlow`, introduced here.
- Training scripts for fitting by maximum likelihood, variational inference, or using contrastive learning for sequential neural posterior estimation ([Greenberg et al., 2019](https://arxiv.org/abs/1905.07488); [Durkan et al., 2020](https://arxiv.org/abs/2002.03712]))

## Installation
```
pip install flowjax
```

## Development
We can install a version for development as follows
```
git clone https://github.com/danielward27/flowjax.git
cd flowjax
pip install -e .[dev]
sudo apt-get install pandoc  # Required for building documentation
```

## Warning
This package is new and may have substantial breaking changes between major releases.
The API for distributions and bijections will be stable, but breaking changes to the
losses and training procedures will be more common. 

## TODO
A few limitations / things that could be worth including in the future:
- Add ability to "reshape" bijections.
- Add amortized variational inference.

## Related
We make use of the [Equinox](https://arxiv.org/abs/2111.00254) package, which facilitates object-oriented programming with Jax. 

## Authors
`flowjax` was written by `Daniel Ward <danielward27@outlook.com>`.

