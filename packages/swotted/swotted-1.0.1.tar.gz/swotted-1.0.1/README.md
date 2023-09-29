# SWoTTeD : An Extension of Tensor Decomposition to Temporal Phenotyping

This repository contains the implementation of **SWoTTeD** (**S**liding **W**ind**o**w for **T**emporal **Te**nsor **D**ecomposition)
  
![Illustration of SwoTTeD Decomposition](./sliding_window_temporal_phenotyping.png)


### Authors

* Hana Sebia, Inria, AIstroSight
* Thomas Guyet, Inria, AIstroSight
* Mike Rye, Inria, AIstroSight

### Overview

***SWoTTeD*** is a tensor decomposition framework to extract temporal phenotypes from structured data. Most recent decomposition models allow extracting phenotypes that only describe snapshots of typical profiles, also called daily phenotypes. However, ***SWoTTeD*** extends the notion of daily phenotype into temporal phenotype describing an arrangement of features over a time window.

The capabilities of the SWoTTeD model are illustrated in the [example notebook](./notebooks/SWoTTeD_module_example.ipynb).


This code implements the SWoTTeD as a [PyTorch Lightning](http://lightning.ai) module that you can embed in you own architecture. The `SWoTTeD` module enables:
* to discover phenotypes through the decomposition of a *3D tensor* (with dimensions: patients, features and time). To deal with patient' data having different duration, the dataset is a collection of pathways (2D matrices);
* to project new patient pathways on discovered phenotypes;
* to predict next events in a pathways.

More documentation about this project and how to use the model is available here: [https://hsebia.gitlabpages.inria.fr/swotted/](https://hsebia.gitlabpages.inria.fr/swotted/).

### How to install

The `pyproject.toml` is the project configuration file for [poetry](https://python-poetry.org/) which enables to create and set up a virtual environment suitable to run ***SWoTTeD***.

```bash
git clone https://gitlab.inria.fr/hsebia/swotted

## In case of the use of poetry
poetry install
poetry shell
```
