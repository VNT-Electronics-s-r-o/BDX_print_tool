import sys
from pathlib import Path

DEV_MODE = False

BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = Path(__file__).resolve().parent

PROGRAM_DIR = (
	Path(sys.executable).resolve().parent
	if getattr(sys, "frozen", False)
	else RESOURCE_DIR
)

ENV_PATH = (
	PROGRAM_DIR.parent / "config" / ".env"
	if getattr(sys, "frozen", False)
	else PROGRAM_DIR / ".env"
)

ICONS_PATH = str(RESOURCE_DIR / "assets") + "/"

SAVE_PATH = r'\\192.168.1.95\\Vyroba\\fencee\\BDX_BD'

PRINTER = "ZDesigner GK420t"

DEVICE_MAP = {
	'BD10': '1610',
	'BD20': '1620',
	'BD30': '1630',
	'BD50': '1650',
	
	'BDX10': '2611',
	'BDX20': '2621',
	'BDX30': '2631',
	'BDX50': '2651',
}

ROLE = "user"