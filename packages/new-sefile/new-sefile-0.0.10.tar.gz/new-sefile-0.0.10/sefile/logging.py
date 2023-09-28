# sefile/logging.py

from sefile import (
    dataclass,
    os, 
    pathlib, 
    logging,
    functools,
    Optional,
    )
from sefile.config import exception_factory


def log_file():
    fullpath = os.path.join(pathlib.Path.cwd(), 'search', 'logs')
    has_dir = os.path.isdir(fullpath)
    
    if has_dir:
        file_target = os.path.join(fullpath, 'log.txt')
        return file_target
    else:
        pathlib.Path(fullpath).mkdir(exist_ok=False)
        file_target = os.path.join(fullpath, 'log.txt')
        return file_target

# create decorator for logging
def do_log(func=None, 
           message: Optional[str] = None, 
           pause: bool = True, 
           format: str = '%(name)s | %(asctime)s %(levelname)s - %(message)s'
           ) -> None:
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if pause:
                return func(*args, **kwargs)
            else:
                try:
                    some_object = func(*args, **kwargs)
                except Exception as error:
                    logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=format,
                            level=logging.ERROR)
                    logging.error(error)
                    raise error
                else:
                    logging.basicConfig(filename=log_file(), 
                            filemode='a+', 
                            format='%(name)s | %(asctime)s %(levelname)s - %(message)s', 
                            level=logging.INFO)
                    logging.info(message)
            return some_object
        return wrapper
    return decorator

@dataclass(frozen=True)
class CustomLogging:
    format_log: str = '%(name)s | %(asctime)s %(levelname)s - %(message)s'

    def __str__(self) -> None:
        return f"({self.format_log})"

    def __repr__(self) -> None:
        return f"{self.__class__.__name__}({self.format_log})"
    
    def info_log(self, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.INFO)
        logging.info(message)
    
    def error_log(self, exception, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.ERROR)
        logging.error(message)
        raise exception_factory(exception, message)
    
    def debug_log(self, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.DEBUG)
        logging.error(message)
    
    def warning_log(self, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.WARNING)
        logging.error(message)
    
    def critical_log(self, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.CRITICAL)
        logging.error(message)
    
    def notset_log(self, message: str) -> None:
        logging.basicConfig(filename=log_file(), filemode='a+', 
                            format=self.format_log,
                            level=logging.NOTSET)
        logging.error(message)

