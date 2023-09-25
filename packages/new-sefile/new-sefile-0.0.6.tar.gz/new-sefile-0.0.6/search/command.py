# search_app/command.py

import os
import pathlib
import typer
from search.controllers import (
    find_logic,
    create_logic,
    read_logic,
    write_logic,
    delete_logic,
    )
from search.callbacks import (
    info_callback,
    file_startswith,
    file_endswith,
    version_callback,
    auto_create_callback,
    )
from search.config import (
    app, 
    FileTypes
    )
from typing import Optional


@app.command(help="Command to [bold yellow]find[/bold yellow] a file by it's name 🔍.")
def find(filename: str = typer.Argument(help="Name of file to [bold yellow]search[/bold yellow] for. :page_facing_up:", 
                                        metavar="FILENAME"),
        path: str = typer.Argument(metavar="PATH", 
                                   help="Directory path for the file to search."),
        startswith: str = typer.Option(default=None, 
                                        help="Search specific file with 'startswith' method :rocket:.", 
                                        is_eager=True, 
                                        callback=file_startswith), 
        endswith: str = typer.Option(default=None, 
                                    help="""Search specific file with 
                                    'endswith' method :sunrise_over_mountains:""", 
                                    is_eager=True, 
                                    callback=file_endswith)) -> None:
    """
    TODO: Define find logic from controllers
    """
    find_logic(filename=filename, path=path, startswith=startswith, endswith=endswith)

@app.command(help="Command to [bold green]create[/bold green] new file followed by a path :cookie:.")
def create(filename: str = typer.Argument(default=None, metavar="FILENAME", 
                                          help="Name of file to [bold green]create[/bold green] a new one. :page_facing_up:"),
           path: str = typer.Argument(default=None, metavar="PATH", 
                                      help="Directory [bold blue]path[/bold blue] for file that has been created. :file_folder:"),
           auto: Optional[bool] = typer.Option(None, "--auto", 
                                               help=f"Automatically create main.py file in {os.path.join(pathlib.Path.home(), 'Create')}", 
                                               is_eager=True,
                                               callback=auto_create_callback)) -> None:
    """
    TODO: Define create logic from controllers
    """
    create_logic(filename=filename, path=path, auto=auto)
@app.command(help="Command to [bold]read[/bold] a file from a directory :book:.")
def read(filename: str = typer.Argument(metavar="FILENAME", 
                                        help="Name of file to read of. :page_facing_up:"),
        path: str = typer.Argument(metavar="PATH", 
                                   help="Directory path of file that want to read of. :file_folder:"),
        read_type: FileTypes = typer.Option(default=FileTypes.text, 
                                       is_flag=True, 
                                       help="Read files according to type selection. :computer:")) -> None:
    """
    TODO: Define read logic from controllers
    """
    read_logic(filename=filename, path=path, read_type=read_type)

@app.command(help="Command to [bold blue]write[/bold blue] one file :page_facing_up:")
def write() -> None:
    """
    TODO: Define write logic from controllers
    """
    write_logic()

@app.command(help="Command to [bold red]delete[/bold red] one or more file :eyes:.")
def delete(filename: str = typer.Argument(metavar="FILENAME", 
                                        help="Name of file to be deleted. :page_facing_up:"),
            path: str = typer.Argument(metavar="PATH", 
                                       help="Directory of file to be deleted. :file_folder:")) -> None:
    """
    TODO: Define write logic from controllers
    """
    delete_logic(filename=filename, path=path)

# main function in here!
@app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", "-v", 
                                                help="Show version of search CLI.", 
                                                is_eager=True, 
                                                callback=version_callback),
         info: Optional[bool] = typer.Option(None, "--info", "-i", 
                                             help="Display info about the application", 
                                             is_eager=True, 
                                             callback=info_callback)) -> None: return



