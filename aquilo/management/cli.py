import os
from importlib import import_module
from inspect import getmembers, isfunction
from types import ModuleType

from aquilo.main import Aquilo

settings = import_module(os.environ.get("AQUILO_SETTINGS_MODULE"))

app = Aquilo(debug=settings.DEBUG)


def validate_home_page(application: str, module: ModuleType):
    if application == "home" or application == "homepage" or application == "index":
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
        raise ValueError(
            "No apps specified."
            "Please specify apps in settings.APPS."
        )

    for application in apps_list:
        app_module = import_module(f"{os.environ.get('AQUILO_APPS_MODULE')}.{application}.pages")
        validate_home_page(application, app_module)
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


def execute_from_command_line(args: list[str]) -> None:
    if len(args) == 1:
        raise ValueError("No command specified.")

    match args[1]:
        case "runserver":
            runserver_command()
        case _:
            raise ValueError("Unknown command.")
