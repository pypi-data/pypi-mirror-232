"""Top-Level package for search file"""
# sefile/__init__.py

import functools
import art
import fnmatch
import inspect
import logging
import npyscreen
import curses
import os
import pathlib
import platform
import rich
import time
import typer
from bullet import (
    colors,
    Bullet, 
    VerticalPrompt,
    SlidePrompt,
    Input,
    )
from colorama import (
    Fore, 
    Back, 
    Style
    )
from dataclasses import dataclass
from enum import Enum
from termcolor import colored
from typing import (
    Optional, 
    Union
    )
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn
    )
from rich.syntax import Syntax

# throw all information about this CLI below
__app_name__ = "Sefile CLI Tool"
__version__ = "0.0.10"
__creator__ = "Faisal Ramadhan"
__creator_email__ = "faisalramadhan1299@gmail.com"
__project_url__ = "https://github.com/kolong-meja"
