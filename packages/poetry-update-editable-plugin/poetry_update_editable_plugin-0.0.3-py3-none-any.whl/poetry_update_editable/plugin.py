from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_update_editable.command import UpdateEditableCommand


def _factory() -> UpdateEditableCommand:
    return UpdateEditableCommand()


class UpdateEditablePlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        """
        Do something
        """
        application.command_loader.register_factory("update-editable", _factory)
