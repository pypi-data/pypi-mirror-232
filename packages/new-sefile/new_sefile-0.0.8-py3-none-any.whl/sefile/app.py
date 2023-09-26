# sefile/app.py

from sefile import (
    __app_name__, 
    command, 
    platform
    )


def main() -> None:
    if platform.uname().system != "Linux":
        raise Exception(f"Program not supported yet for '{platform.uname().system}' system.")
    else:
        command.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()