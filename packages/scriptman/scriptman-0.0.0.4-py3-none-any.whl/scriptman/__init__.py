import atexit

from scriptman.cleanup import CleanUpHandler
from scriptman.cli import CLIHandler
from scriptman.csv import CSVHandler
from scriptman.database import DatabaseHandler
from scriptman.directories import DirectoryHandler
from scriptman.etl import ETLHandler
from scriptman.logs import LogHandler
from scriptman.scripts import ScriptsHandler
from scriptman.selenium import Interaction, SeleniumHandler
from scriptman.settings import settings

atexit.register(CleanUpHandler)
