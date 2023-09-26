# poetry-plugin-configurable-venv-location

## Description


*poetry-plugin-configurable-venv-location* is a [plugin](https://python-poetry.org/docs/master/plugins/) for [poetry](https://python-poetry.org/), the Python packaging and dependency manager. It allows one to specify a different virtual env locaton when using `virtualenvs.in-project` is set to `true`.

### Installation

Follow poetry's [plugin installation instructions](https://python-poetry.org/docs/master/plugins/#using-plugins), replacing `poetry-plugin` with `poetry-plugin-configurable-venv-location`.


## Usage

Create a file called `.poetry_venv_path` in the same folder as your `pyproject.toml` containing path to your virtual env. e.g.:

```
/some/path/to/a/.venv
```

Also set the following config option in poetry:

```bash
poetry config virtualenvs.in-project true
```


## Notes

This plugin is a way to workaround poetry limitation [#1579](https://github.com/python-poetry/poetry/issues/1579).