# search/config.py

import typer
import os
from dotenv import load_dotenv
from enum import Enum


load_dotenv()
app_level = os.environ.get('APP_LEVEL')
# create typer object.
app = typer.Typer(help="[bold green]Easiest[/bold green] way to [bold yellow]find[/bold yellow], [bold]read[/bold], [bold green]create[/bold green], [bold cyan]write[/bold cyan], and [bold red]delete[/bold red] a file :file_folder:.", 
                add_completion=False,
                pretty_exceptions_show_locals=False, 
                pretty_exceptions_enable=True,
                rich_markup_mode='rich')

class FileTypes(Enum):
    text = 'text'
    python = 'python'
    javascript = 'javascript'
    typescript = 'typescript'
    go = 'go'
    php = 'php'
    bash = 'bash'
    css = 'css'
    html = 'html'
    rust = 'rust'

