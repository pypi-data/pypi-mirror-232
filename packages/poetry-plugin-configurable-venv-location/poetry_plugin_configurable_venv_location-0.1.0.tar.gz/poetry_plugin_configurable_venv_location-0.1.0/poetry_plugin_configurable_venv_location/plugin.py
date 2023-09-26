from pathlib import Path

from cleo.io.io import IO
from cleo.helpers import option

from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
import poetry.utils.env as poetry_utils_env

VENV_LOCATION_FILE = ".poetry_venv_path"


def in_project_venv(self) -> Path:
    alt_venv_loc_file = self._poetry.pyproject_path.parent / VENV_LOCATION_FILE
    if alt_venv_loc_file.exists():
        return Path(alt_venv_loc_file.read_text().strip())
    else:
        return self._poetry.file.path.parent / ".venv"



class ConfigurableVenvLocationPlugin(Plugin):
    def activate(self, poetry: Poetry, io: IO):
        poetry_utils_env.EnvManager.in_project_venv = property(in_project_venv)
         
