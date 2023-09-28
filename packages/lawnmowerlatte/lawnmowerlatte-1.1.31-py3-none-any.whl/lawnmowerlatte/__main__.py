import sys


def ingress():
    args = sys.argv

    if len(args) > 1:
        module = args[1]
        sys.argv = args[2:]
        eval(f"import {module} as target")
        print(f"Delegating to {module}: {sys.argv}")
        breakpoint()
        target.ingress()
    else:
        print(f"Please specify a subcommand")


if __name__ == "__main__":
    ingress()
