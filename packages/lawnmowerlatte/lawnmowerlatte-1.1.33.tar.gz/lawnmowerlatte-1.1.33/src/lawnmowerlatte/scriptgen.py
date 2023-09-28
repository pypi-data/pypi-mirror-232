""" A simple implementation of the Script class which can generate scripts from template
>>> m = ScriptGen("")
>>> isinstance(m, ScriptGen)
True
"""

import os
import sys
import logging
from jinja2 import Environment, FileSystemLoader

from lawnmowerlatte.script import Script
from lawnmowerlatte.version import version

log = logging.getLogger()


class ScriptGen(Script):
    """scriptgen: A simple implementation of the Script class which can generate scripts from template
    >>> isinstance(script, ScriptGen)
    True
    >>> isinstance(script, Script)
    True
    >>> issubclass(script.__class__, Script)
    True
    """

    options = [
        {
            "args": ["--template"],
            "help": "generate a new script based on the template",
            "action": "store_true",
        },
    ]

    def fn(self):
        if self.args.template:
            script_details = self.interactive_script_generator()
            self.render_script(script_details)
            return

        super().fn()

    def interactive_script_generator(self):
        details = {
            "args": [],
            "errors": [],
        }

        details["filename"] = input("Enter the filename: ")
        details["description"] = input("Enter the description of the script: ")
        details["class"] = input("Enter the class name of the script: ")

        try:
            print("Enter argument details: (^C to continue)")
            while True:
                arg = {"flags": [], "parameters": []}

                name = input("Argument name: ")
                arg["flags"].append(f"--{name}")

                letter = input("Argument letter (optional): ")
                if letter:
                    arg["flags"].append(f"-{letter}")

                arg["help"] = input("Help text: ")

                is_boolean = input("Is this a boolean flag? [Y/N]")
                if is_boolean and is_boolean[0].lower() == "y":
                    arg["parameters"].append({"key": "action", "value": "'store_true'"})

                details["args"].append(arg)
                print(f"Argument '{arg['flags'][0]}' completed.\n")
        except KeyboardInterrupt:
            print()
            print(f"{len(details['args'])} arguments accepted")
            print()

        try:
            print("Enter error messages: (^C to continue)")
            while True:
                details["errors"].append(input("Enter error message: "))
        except KeyboardInterrupt:
            print()
            print(f"{len(details['errors'])} errors accepted")
            print()

        return details

    def render_script(self, script_parameters):
        file_loader = FileSystemLoader(
            os.path.join(
                os.path.dirname(sys.modules[self.__module__].__file__), "templates"
            )
        )
        env = Environment(loader=file_loader)
        template = env.get_template("script.jinja")
        rendered = template.render(script_parameters)

        with open(script_parameters["filename"], "w") as f:
            f.write(rendered)

        print(rendered)

        print(f"Run `python3 {script_parameters['filename']} --help` to confirm")


ingress = ScriptGen
