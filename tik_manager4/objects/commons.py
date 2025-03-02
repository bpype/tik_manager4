"""Commons module for tik_manager4 package."""

from pathlib import Path
import shutil

from tik_manager4.core.settings import Settings
from tik_manager4 import defaults


class Commons:
    """Class to handle the common settings and user data"""
    exportSettings = None
    importSettings = None
    user_defaults = None
    project_settings = None
    users = None
    template = None
    structures = None
    metadata = None

    def __init__(self, folder_path):
        """Initialize the Commons class."""
        super().__init__()
        self._folder_path = folder_path
        self.is_valid = self._validate_commons_folder()

    @property
    def folder_path(self):
        """Return the folder path."""
        return str(self._folder_path)

    def _validate_commons_folder(self):
        """Make sure the 'commons folder' contains the necessary setting files.

        Returns:
            bool: True if the folder is valid, False otherwise.
        """
        # copy the default template files to common folder
        for default_file in defaults.all:
            _default_file_path = Path(default_file)
            base_name = _default_file_path.name
            _common_file_path = Path(self._folder_path, base_name)
            if not _common_file_path.is_file():
                try:
                    shutil.copy(default_file, str(_common_file_path))
                except PermissionError:
                    return False

        self.category_definitions = Settings(
            file_path=str(Path(self._folder_path, "category_definitions.json"))
        )
        self.user_defaults = Settings(
            file_path=str(Path(self._folder_path, "user_defaults.json"))
        )
        self.project_settings = Settings(
            file_path=str(Path(self._folder_path, "project_settings.json"))
        )
        self.preview_settings = Settings(
            file_path=str(Path(self._folder_path, "preview_settings.json"))
        )
        self.users = Settings(
            file_path=str(Path(self._folder_path, "users.json"))
        )
        self.template = Settings(
            file_path=str(Path(self._folder_path, "templates.json"))
        )
        self.structures = Settings(
            file_path=str(Path(self._folder_path, "structures.json"))
        )
        self.metadata = Settings(
            file_path=str(Path(self._folder_path, "metadata.json"))
        )
        self.management_settings = Settings(
            file_path=str(Path(self._folder_path, "management_settings.json"))
        )
        return True

    def check_user_permission_level(self, user_name):
        """Return the permission level for given user.

        Args:
            user_name (str): The name of the user.

        Returns:
            int: The permission level of the user.
        """
        return self.users.get_property(user_name).get("permissionLevel", 0)

    def get_user_email(self, user_name):
        """Return the email of the user.

        Args:
            user_name (str): The name of the user.

        Returns:
            str: The email of the user.
        """
        return self.users.get_property(user_name).get("email", "")

    def get_users(self):
        """Return the list of all active users."""
        return self.users.keys

    def get_project_structures(self):
        """Return list of available project structures defined in defaults."""
        return self.structures.keys

    def collect_common_modules(self, dcc_name, module_type):
        """Collect the available studio-specific dcc modules."""
        # check the <common_folder>/<dcc_name>/modules folder for available python files.
        plugin_path = Path(self._folder_path, "plugins", dcc_name, module_type)
        plugin_path.mkdir(parents=True, exist_ok=True)
        return plugin_path.glob("*.py")
