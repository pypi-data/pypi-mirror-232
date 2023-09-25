# search_app/app.py

import platform
from search import command, __app_name__


def main() -> None:
    if platform.uname().system != "Linux":
        raise Exception(f"Program not supported yet for '{platform.uname().system}' system.")
    else:
        command.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()