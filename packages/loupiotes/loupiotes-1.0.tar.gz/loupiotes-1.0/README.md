# loupiotes: a Bayesian starspot modelling tool

[![Documentation Status](https://readthedocs.org/projects/loupiotes/badge/?version=latest)](https://loupiotes.readthedocs.io/en/latest/?badge=latest)

## What is loupiotes ?

Using modern sampling method enabling GPU scaling, ``loupiotes`` is 
mainly dedicated to perform Bayesian starspot modelling. 
Building upon the powerful framework provided by the 
[PyMC](https://www.pymc.io/welcome.html) framework, 
it implements starspots model exploration through 
Maximum a-posteriori (MAP) analysis and Hamiltonian Monte-Carlo 
(HMC) sampling.  

## Getting started

### Prerequisites

``loupiotes`` is written in Python3. 
The following Python package are necessary to use it : 
- pymc
- arviz
- numpy
- scipy
- matplotlib
- numba
- tqdm

### Installation

``loupiotes`` does not have a PyPI or conda-forge packaged version yet.
You will have to clone the online repository and run at the root of
the downloaded directory: 

``pip install .``

### Documentation

An [online documentation](https://loupiotes.readthedocs.io/en/latest/) 
with tutorials and API description is available.

## Author

* **Sylvain N. Breton** - Maintainer - (INAF-OACT, Catania, Italy)

## Acknowledgements 

If you use ``loupiotes`` in your work, please provide a link to
the GitLab repository.

## References 

The models implemented by ``loupiotes`` are described in the following publications:
- [Lanza et al. (2007), Astronomy & Astrophysics, 464, 741L](https://ui.adsabs.harvard.edu/abs/2007A%26A...464..741L/abstract). 
- [Lanza (2016), Cartography of the Sun and the Stars, Lecture Notes in Physics, Volume 914](https://ui.adsabs.harvard.edu/abs/2016LNP...914...43L/abstract).
