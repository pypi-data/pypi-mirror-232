# sefile/command.py

from sefile import (
    pathlib, 
    typer, 
    Optional,
    )
from sefile.controllers import Controller
from sefile.callbacks import Callback
from sefile.config import (
    app, 
    FileTypes
    )


@app.command(help="Command to [bold yellow]find[/bold yellow] a file by it's name 🔍.")
def find(filename: str = typer.Argument(help="Name of file to [bold yellow]search[/bold yellow] for. :page_facing_up:", 
                                        metavar="FILENAME"),
        path: str = typer.Argument(metavar="PATH", 
                                   help="Directory path for the file to search."),
        startswith: str = typer.Option(default=None, 
                                        help="Search specific file with 'startswith' method :rocket:.", 
                                        is_eager=True, 
                                        callback=Callback.startswith_search), 
        endswith: str = typer.Option(default=None, 
                                    help="""Search specific file with 
                                    'endswith' method :sunrise_over_mountains:""", 
                                    is_eager=True, 
                                    callback=Callback.endswith_search)) -> None:
    """
    TODO: Define find logic from controllers
    """
    find_logic = Controller(filename=filename, path=path)
    find_logic.find_controller(startswith=startswith, endswith=endswith)

@app.command(help="Command to [bold green]create[/bold green] new file followed by a path :cookie:.")
def create(filename: str = typer.Argument(default=None, metavar="FILENAME", 
                                          help="Name of file to [bold green]create[/bold green] a new one. :page_facing_up:"),
           path: str = typer.Argument(default=None, metavar="PATH", 
                                      help="Directory [bold blue]path[/bold blue] for file that has been created. :file_folder:"),
           auto: Optional[bool] = typer.Option(None, "--auto", 
                                               help=f"Automatically create simple (Python, Javascript, and Go) project in '{pathlib.Path.home()}'", 
                                               is_eager=True,
                                               callback=Callback.auto_create_callback)) -> None:
    """
    TODO: Define create logic from controllers
    """
    create_logic = Controller(filename=filename, path=path)
    create_logic.create_controller(auto=auto)

@app.command(help="Command to [bold]read[/bold] a file from a directory :book:.")
def read(filename: str = typer.Argument(metavar="FILENAME", 
                                        help="Name of file to read of. :page_facing_up:"),
        path: str = typer.Argument(metavar="PATH", 
                                   help="Directory path of file that want to read of. :file_folder:"),
        read_type: FileTypes = typer.Option(default=FileTypes.text.value, 
                                       is_flag=True, 
                                       help="Read files according to type selection. :computer:")) -> None:
    """
    TODO: Define read logic from controllers
    """
    read_logic = Controller(filename=filename, path=path)
    read_logic.read_controller(read_type=read_type)
    # read_logic(filename=filename, path=path, read_type=read_type)

@app.command(help="Command to [bold blue]write[/bold blue] one file :page_facing_up:")
def write() -> None:
    """
    TODO: Define write logic from controllers
    """
    Controller.write_controller()

@app.command(help="Command to [bold red]delete[/bold red] one or more file :eyes:.")
def delete(filename: str = typer.Argument(metavar="FILENAME", 
                                        help="Name of file to be deleted. :page_facing_up:"),
            path: str = typer.Argument(metavar="PATH", 
                                       help="Directory of file to be deleted. :file_folder:")) -> None:
    """
    TODO: Define write logic from controllers
    """
    delete_logic = Controller(filename=filename, path=path)
    delete_logic.delete_controller()

# main function in here!
@app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", "-v", 
                                                help="Show version of search CLI.", 
                                                is_eager=True, 
                                                callback=Callback.version_callback)) -> None: return



