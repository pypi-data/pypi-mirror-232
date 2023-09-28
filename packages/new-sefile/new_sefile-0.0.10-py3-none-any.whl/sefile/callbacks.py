# sefile/callback.py

from sefile import (
    art,
    rich,
    typer,
    colored,
    dataclass,
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
from sefile.logging import CustomLogging
from sefile.config import exception_factory


# define private instance for CustomLog class
_some_log = CustomLogging(format_log='%(name)s | %(asctime)s %(levelname)s - %(message)s')

@dataclass(frozen=True)
class _ProjectType:
    dir_path: str

    def __str__(self) -> None:
        return f"({self.dir_path})"
    
    def __repr__(self) -> None:
        return f"{self.__class__.__name__}({self.dir_path})"

    def _py_project(self) -> None:
        os.mkdir(self.dir_path)
        # create sub directory
        for subdir in ["src", "tests"]:
            os.makedirs(os.path.join(self.dir_path, subdir))
        # create files in src directory
        for src_file in ['__init__.py', 'main.py']:
            open(os.path.join(os.path.join(self.dir_path, 'src'), src_file), 'x')
        # create files in tests directory
        for tests_file in ['__init__.py', 'test.py']:
            open(os.path.join(os.path.join(self.dir_path, 'tests'), tests_file), 'x')
        # create required file on project.
        for req_file in ['LICENSE.md', 'README.md', 'requirements.txt']:
            open(os.path.join(self.dir_path, req_file), 'x')
        rich.print(f"All [bold green]Done![/bold green] ✅, path: '{self.dir_path}'")
    
    def _js_project(self) -> None:
        os.mkdir(self.dir_path)
        # create sub directory
        for subdir in ["src", "tests", "public"]:
            os.makedirs(os.path.join(self.dir_path, subdir))
        # create files in src directory
        for src_file in ["index.js", "app.js"]:
            open(os.path.join(os.path.join(self.dir_path, 'src'), src_file), 'x')
        # create files in public directory
        for public_file in ['index.html', 'style.css', 'script.js']:
            open(os.path.join(os.path.join(self.dir_path, 'public'), public_file), 'x')
        # create files in tests directory
        for tests_file in ['service.test.js', 'component.test.js']:
            open(os.path.join(os.path.join(self.dir_path, 'tests'), tests_file), 'x')
        # create required file on project
        for req_file in ['LICENSE.md', 'README.md', 'package.json']:
            open(os.path.join(self.dir_path, req_file), 'x')
        rich.print(f"All [bold green]Done![/bold green] ✅, path: {self.dir_path}")
    
    def _go_project(self) -> None:
        os.mkdir(self.dir_path)
        # create sub directory
        for subdir in ["src", "tests"]:
            os.makedirs(os.path.join(self.dir_path, subdir))
        # create files in src directory
        for src_file in ["main.go", "utils.go"]:
            open(os.path.join(os.path.join(self.dir_path, 'src'), src_file), 'x')
        # create files in tests directory
        for tests_file in ["test.go"]:
            open(os.path.join(os.path.join(self.dir_path, 'tests'), tests_file), 'x')
        # create required file on project
        for req_file in ["LICENSE.md", "README.md", "config.go"]:
            open(os.path.join(self.dir_path, req_file), 'x')
        rich.print(f"All [bold green]Done![/bold green] ✅, path: {self.dir_path}")

@dataclass
class Callback:
    @staticmethod
    def _create_project(choice: str) -> None:
        # input project name
        project_name = Input(f"What's the name of the {choice} project? ", word_color=colors.foreground["yellow"])
        project_name_result = project_name.launch()
        # input project directory
        project_dir = Input(f"Where do you want to save this {project_name_result}? ", word_color=colors.foreground["yellow"])
        project_dir_result = project_dir.launch()
        # check if project dir exists in your PC
        if not pathlib.Path(project_dir_result).is_dir():
            raise exception_factory(FileNotFoundError, f"File or Path not found, path: '{project_dir_result}'")
        else:    
            project_path = os.path.join(project_dir_result, project_name_result)
        
        if os.path.exists(project_path):
            raise exception_factory(FileExistsError, f"Folder exists: '{project_path}'")
        else:
            if "Python" in choice:
                _python_project = _ProjectType(dir_path=project_path)
                _python_project._py_project()
            elif "Javascript" in choice:
                _javascript_project = _ProjectType(dir_path=project_path)
                _javascript_project._js_project()
            elif "Go" in choice:
                _golang_project = _ProjectType(dir_path=project_path)
                _golang_project._go_project()
            else:
                pass

    def version_callback(self, value: bool) -> None:
        if value:
            ascii_art = art.text2art("SEFILE", font="swampland", chr_ignore=True)
            print(f"\n{colored(ascii_art, color='green', attrs=['bold'])}\n")
            rich.print(f"""[yellow]{'*'*40}|[bold]Information[/bold]|{'*'*40}[/yellow]\
                    \n\n[bold]App name[/bold]: {__app_name__}\
                    \n[bold]{__app_name__} version[/bold]: {__version__}\
                    \n[bold]Creator name[/bold]: {__creator__}\
                    \n[bold]Creator email[/bold]: {__creator_email__}\
                    \n[bold]Creator github[/bold]: {__project_url__}\
                    """)
            raise typer.Exit()
    
    def auto_create_callback(self, value: bool) -> None:
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
                Callback._create_project(choice=result)
            elif result == "☕ Javascript":
                Callback._create_project(choice=result)
            elif result == "🐼 Go":
                Callback._create_project(choice=result)
            else:
                print("See ya! 👋")
                raise typer.Exit()
    
    def startswith_search(self, value: str) -> None:
        if value:
            dir_start = Input(f"From where do you want to find '{value}' file? ", word_color=colors.foreground["yellow"])
            dir_start_result = dir_start.launch()

            if not pathlib.Path(dir_start_result).is_dir():
                raise exception_factory(FileNotFoundError, f"File or Path not found, path: '{dir_start_result}'")
            else:
                total_file = 0
                with Progress(
                    SpinnerColumn(spinner_name="dots9"),
                    TextColumn("[progress.description]{task.description}"),
                    auto_refresh=True,
                    transient=True,
                    get_time=None,
                ) as progress:
                    task = progress.add_task(f"Find file startswith '{value}' from {dir_start_result}", total=100_000)
                    for root, dirs, files in os.walk(dir_start_result, topdown=True):
                        for some_file in files:
                            if some_file.startswith(value):
                                total_file += 1
                                fullpath = os.path.join(f"[white]{root}[/white]", f"[bold yellow]{some_file}[/bold yellow]")
                                rich.print(f"{fullpath}")
                                progress.advance(task)
                if total_file < 1:
                    raise exception_factory(FileNotFoundError, f"File startswith '{value}' not found from '{dir_start_result}' path")
                else:
                    rich.print(f"Search file startswith '{value}' [bold green]success![/bold green]")
                    raise typer.Exit()
    
    def endswith_search(self, value: str) -> None:
        if value:
            dir_start = Input(f"From where do you want to find '{value}' file? ", word_color=colors.foreground["yellow"])
            dir_start_result = dir_start.launch()

            if not pathlib.Path(dir_start_result).is_dir():
                raise exception_factory(FileNotFoundError, f"File or Path not found, path: '{dir_start_result}'")
            else:
                total_file = 0
                with Progress(
                    SpinnerColumn(spinner_name="dots9"),
                    TextColumn("[progress.description]{task.description}"),
                    auto_refresh=True,
                    transient=True,
                    get_time=None,
                ) as progress:
                    task = progress.add_task(f"Find file endswith '{value}' from {dir_start_result}", total=100_000)
                    for root, dirs, files in os.walk(dir_start_result, topdown=True):
                        for some_file in files:
                            if some_file.endswith(value):
                                total_file += 1
                                fullpath = os.path.join(f"[white]{root}[/white]", f"[bold yellow]{some_file}[/bold yellow]")
                                rich.print(f"{fullpath}")
                                progress.advance(task)
                if total_file < 1:
                    raise exception_factory(FileNotFoundError, f"File endswith '{value}' not found from '{dir_start_result}' path")
                else:
                    rich.print(f"Search file startswith '{value}' [bold green]success![/bold green]")
                    raise typer.Exit()
    