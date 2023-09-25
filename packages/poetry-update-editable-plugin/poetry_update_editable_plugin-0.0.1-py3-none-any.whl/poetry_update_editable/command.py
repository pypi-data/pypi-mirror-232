from typing import ClassVar

from cleo.helpers import Option, option
from poetry.console.commands.installer_command import InstallerCommand


class UpdateEditableCommand(InstallerCommand):
    name = "update-editable"
    description = (
        "Updates all packages marked as editable (develop = true) in your project's"
        " pyproject.toml"
    )

    def __init__(self) -> None:
        self.options = [
            *InstallerCommand._group_dependency_options(),
            option(
                "dry-run",
                None,
                "Output the operations buy do not execute anything "
                "(implicity enables --verbose).",
            ),
        ]

        return super().__init__()

    def handle(self) -> int:
        # Get all editable package (develop = True)
        repository = self.poetry.locker.locked_repository()
        packages = [package for package in repository.packages if package.develop]

        # Setup installer options
        self.installer.whitelist({package.name: "*" for package in packages})
        self.installer.only_groups(self.activated_groups)
        self.installer.dry_run(self.option("dry-run"))

        # Force update
        self.installer.update(True)

        # Run installation
        return self.installer.run()
