# sefile/callback.py

from sefile import (
    art,
    rich,
    typer,
    colored,
    os,
    pathlib,
    Progress,
    SpinnerColumn,
    TextColumn,
    __app_name__,
    __version__,
    __creator__,
    __creator_email__,
    __project_url__,
    colors,
    Bullet,
    Input,
    )
from sefile.logs import CustomLog
from sefile.logs import exception_factory


def _create_project(choice: str):
    some_input = Input(f"What's the name of the {choice} project? ", word_color=colors.foreground["yellow"])
    input_result = some_input.launch()
    project_dir = os.path.join(pathlib.Path.home(), input_result)
    
    if os.path.exists(project_dir):
        raise exception_factory(FileExistsError, f"Folder exists: '{project_dir}'")
    else:
        if "Python" in choice:
            os.mkdir(project_dir)
            # create sub directory
            for subdir in ["src", "tests"]:
                os.makedirs(os.path.join(project_dir, subdir))
            # create files in src directory
            for src_file in ['__init__.py', 'main.py']:
                open(os.path.join(os.path.join(project_dir, 'src'), src_file), 'x')
            # create files in tests directory
            for tests_file in ['__init__.py', 'test.py']:
                open(os.path.join(os.path.join(project_dir, 'tests'), tests_file), 'x')
            # create required file on project.
            for req_file in ['LICENSE.md', 'README.md', 'requirements.txt']:
                open(os.path.join(project_dir, req_file), 'x')
            rich.print(f"All [bold green]Done![/bold green] ✅, path: {project_dir}")
        elif "Javascript" in choice:
            os.mkdir(project_dir)
            # create sub directory
            for subdir in ["src", "tests", "public"]:
                os.makedirs(os.path.join(project_dir, subdir))
            # create files in src directory
            for src_file in ["index.js", "app.js"]:
                open(os.path.join(os.path.join(project_dir, 'src'), src_file), 'x')
            # create files in public directory
            for public_file in ['index.html', 'style.css', 'script.js']:
                open(os.path.join(os.path.join(project_dir, 'public'), public_file), 'x')
            # create files in tests directory
            for tests_file in ['service.test.js', 'component.test.js']:
                open(os.path.join(os.path.join(project_dir, 'tests'), tests_file), 'x')
            # create required file on project
            for req_file in ['LICENSE.md', 'README.md', 'package.json']:
                open(os.path.join(project_dir, req_file), 'x')
            rich.print(f"All [bold green]Done![/bold green] ✅, path: {project_dir}")
        else:
            os.mkdir(project_dir)
            # create sub directory
            for subdir in ["src", "tests"]:
                os.makedirs(os.path.join(project_dir, subdir))
            # create files in src directory
            for src_file in ["main.go", "utils.go"]:
                open(os.path.join(os.path.join(project_dir, 'src'), src_file), 'x')
            # create files in tests directory
            for tests_file in ["test.go"]:
                open(os.path.join(os.path.join(project_dir, 'tests'), tests_file), 'x')
            # create required file on project
            for req_file in ["LICENSE.md", "README.md", "config.go"]:
                open(os.path.join(project_dir, req_file), 'x')
            rich.print(f"All [bold green]Done![/bold green] ✅, path: {project_dir}")

# define private instance for CustomLog class
_some_log = CustomLog(format_log='%(name)s | %(asctime)s %(levelname)s - %(message)s')

# create version callback function.
def version_callback(value: bool) -> None:
    if value:
        rich.print(f"[bold]{__app_name__} version[/bold]: {__version__}")
        raise typer.Exit()

# cretae info callback function.
def info_callback(value: bool) -> None:
    if value:
        # show logo
        ascii_art = art.text2art("SEFILE", font="swampland", chr_ignore=True)
        print(f"\n{colored(ascii_art, color='green', attrs=['bold'])}\n")
        # create long text
        output = f"""[yellow]{'*'*40}|[bold]Information[/bold]|{'*'*40}[/yellow]\
                    \n\n[bold]App name[/bold]: {__app_name__}\
                    \n[bold]{__app_name__} version[/bold]: {__version__}\
                    \n[bold]Creator name[/bold]: {__creator__}\
                    \n[bold]Creator email[/bold]: {__creator_email__}\
                    \n[bold]Creator github[/bold]: {__project_url__}\
                """
        rich.print(output)
        raise typer.Exit()

def auto_create_callback(value: bool) -> None:
    if value:
        some_cli = Bullet(
            "What's simple project you want to create? ", 
            choices=["🐍 Python", "☕ Javascript", "🐼 Go", "❌ Cancel"],
            bullet=" >",
            margin=2,
            bullet_color=colors.bright(colors.foreground["cyan"]),
            background_color=colors.background["default"],
            background_on_switch=colors.background["default"],
            word_color=colors.foreground["white"],
            word_on_switch=colors.foreground["white"],
            )
        result = some_cli.launch()

        if result == "🐍 Python":
            _create_project(choice=result)
        elif result == "☕ Javascript":
            _create_project(choice=result)
        elif result == "🐼 Go":
            _create_project(choice=result)
        else:
            print("See ya! 👋")
            raise typer.Exit()

def file_startswith(value: str) -> None:
    if value:
        # user home root.
        user_home_root = pathlib.Path.home()
        # scan all root from user home root.
        scanning_directory = os.walk(user_home_root, topdown=True)
        file_total = 0
        # iterate all directory.
        with Progress(
            SpinnerColumn(spinner_name="dots9"),
            TextColumn("[progress.description]{task.description}"),
            auto_refresh=True, 
            transient=True,
            get_time=None,
            ) as progress:
            task = progress.add_task(f"Find file startswith '{value}' from {user_home_root}", total=100_000_000)
            for root, dirs, files in scanning_directory:
                for file in files:
                    # filter file same as filename param.
                    if file.startswith(value):
                        file_total += 1
                        # join the root and file.
                        root = f"[white]{root}[/white]"
                        file = f"[bold yellow]{file}[/bold yellow]"
                        fullpath = os.path.join(root, file)
                        rich.print(f"{fullpath}")
                        progress.advance(task)
        
        if file_total != 0:
            rich.print(f"Search file startswith '{value}' [bold green]success![/bold green]")
            raise typer.Exit()
        else:
            raise exception_factory(FileNotFoundError, f"File '{value}' not found.")

def file_endswith(value: str) -> None:
    if value:
        # user home root.
        user_home_root = pathlib.Path.home()
        # scan all root from user home root.
        scanning_directory = os.walk(user_home_root, topdown=True)
        file_total = 0
        with Progress(
            SpinnerColumn(spinner_name="dots9"),
            TextColumn("[progress.description]{task.description}"),
            auto_refresh=True, 
            transient=True,
            ) as progress:
            task = progress.add_task(f"Find file startswith '{value}' from {user_home_root}", total=100_000_000)
            # iterate all directory.
            for root, dirs, files in scanning_directory:
                for file in files:
                    # filter file same as filename param.
                    if file.endswith(value):
                        file_total += 1
                        root = f"[white]{root}[/white]"
                        file = f"[bold yellow]{file}[/bold yellow]"
                        # join the root and file.
                        fullpath = os.path.join(root, file)
                        rich.print(f"{fullpath}")
                        progress.advance(task)

        if file_total != 0:
            rich.print(f"Search file endswith '{value}' [bold green]success![/bold green]")
            raise typer.Exit()
        else:
            raise exception_factory(FileNotFoundError, f"File '{value}' not found.")
    