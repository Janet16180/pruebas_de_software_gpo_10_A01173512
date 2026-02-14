# Pruebas de Software y Aseguramiento de la Calidad

This repository contains all the homework assignments for the course Pruebas de Software y Aseguramiento de la Calidad (Gpo 10).

## Project structure

The homework is organized in numbered directories. Each directory contains the exercises for a specific assignment.

- 1_ejercicios_programacion: First set of programming exercises
  - 1_compute_statistics
  - 2_converter
  - 3_count_words

## Development setup

This project uses uv as the package manager and ruff as the linter. Setting up the virtual environment is not mandatory, this is just my personal setup for development. If you want to replicate it, make sure you have uv installed and then run:

```
uv sync
```

This will create a virtual environment and install all the dependencies.

## Linting

I am using ruff to apply linting to the codebase. Ruff already includes PEP8 style checks by default, so the code follows the standard Python style guide. Additionally, I have enabled some extra checks that ruff offers, since it is more strict than the default PEP8 rules. For example, I have enabled type annotation checks (ANN) to ensure that functions have proper type hints.

The linting configuration can be found in the pyproject.toml file.

## Pre-commit hooks

The repository has pre-commit hooks configured to run ruff automatically before each commit. This ensures that all code pushed to the repository follows the linting rules. The hooks include:

- ruff: checks and fixes linting issues
- ruff-format: formats the code
- yamllint: validates yaml files

To install the pre-commit hooks locally, run:

```
prek install
```

This project uses [prek](https://github.com/j178/prek), a fast pre-commit implementation written in Rust.
