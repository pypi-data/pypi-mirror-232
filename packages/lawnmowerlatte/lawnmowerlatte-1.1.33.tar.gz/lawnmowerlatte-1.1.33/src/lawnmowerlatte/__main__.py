"""Ingress"""

import sys

from lawnmowerlatte.script import Script


def ingress():
    args = sys.argv

    if len(args) > 1:
        name = args[1]
        sys.argv = [args[1]] + args[2:]

        print(f"Delegating execution to lawnmowerlatte.{name}: {sys.argv}")

        try:
            exec(f"from lawnmowerlatte import {name}")
        except Exception as e:
            print(f"Couldn't delegate module {name}: {e}")

        fullname = f"lawnmowerlatte.{name}"
        assert fullname in sys.modules, f"Module was not imported correctly"
        target = sys.modules[fullname]
        assert type(target).__name__ == "module", f"Target was not a module: {target}"
        assert hasattr(target, "ingress"), f"Target does not have an ingress"
        ingress = target.ingress
        assert callable(ingress), f"Ingress is not callable"

        if issubclass(ingress, Script):
            script = ingress()
            script.main()
        else:
            ingress()
    else:
        print(f"Please specify a subcommand")


if __name__ == "__main__":
    ingress()
