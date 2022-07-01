import os
import sys
from importlib import import_module
from inspect import getmembers, isfunction
from pathlib import Path
from types import ModuleType

from aquilo.main import Aquilo

settings = import_module(os.environ.get("AQUILO_SETTINGS_MODULE"))

app = Aquilo(debug=settings.DEBUG)


def validate_home_page(application: str, apps_list: list[str], module: ModuleType):
    if application == apps_list[0]:
        homepage_function = list()

        for member in getmembers(module, isfunction):
            if member[0].startswith("page_"):
                name = member[1].__name__.split("page_")

                if len(name) == 1:
                    raise ValueError("Invalid page name.")
                homepage_function.append(member[1])

        if len(homepage_function) > 1:
            raise ValueError(
                "The homepage application must have only one function."
                "Please remove the other functions."
            )


def runserver_command():
    apps_list: list[str] = settings.APPS

    if len(apps_list) == 0:
        raise ValueError("No apps specified." "Please specify apps in settings.APPS.")

    for application in apps_list:
        try:
            app_module = import_module(
                f"{os.environ.get('AQUILO_APPS_MODULE')}.{application}.pages"
            )
        except ImportError as exc:
            raise ValueError(
                f"{application} module was not found in apps. "
                "Please check the spelling."
            ) from exc
        validate_home_page(application, apps_list, app_module)
        register_pages(application, app_module)

    app.run()


def register_pages(application: str, module: ModuleType):
    for member in getmembers(module, isfunction):
        if member[0].startswith("page_"):
            name = member[1].__name__.split("page_")

            if len(name) == 1:
                raise ValueError("Invalid page name.")

            member[1].__name__ = f"page_{application}_{name[1]}"
            app.page(member[1])


def startapp_command(app_name: str):
    app_directory = os.environ.get("AQUILO_APPS_MODULE").replace(".", os.sep)
    new_app_directory = Path(app_directory + os.sep + app_name)

    if os.path.exists(new_app_directory):
        raise ValueError("App already exists.")

    os.makedirs(new_app_directory)

    with open(f"{new_app_directory}/__init__.py", "w") as init:
        init.write("")

    with open(f"{new_app_directory}/pages.py", "w") as pages:
        pages.write("from aquilo import build\n\n")


def execute_from_command_line(args: list[str]) -> None:
    if len(args) == 1:
        raise ValueError("No command specified.")

    match args[1]:
        case "runserver":
            runserver_command()
        case "startapp":
            try:
                startapp_command(args[2])
            except IndexError:
                raise ValueError("No app name specified.")
        case _:
            raise ValueError("Invalid command.")


def main():
    execute_from_command_line(sys.argv)