from pathlib import Path
import sys


if "__compiled__" in dir():
    ROOT_PATH = Path(sys.argv[0]).resolve().parent
else:
    ROOT_PATH = Path(__file__).resolve().parent
LOGS_DIR = ROOT_PATH / "logs"
TEMPLATE_PATH = ROOT_PATH / "config.toml.template"
