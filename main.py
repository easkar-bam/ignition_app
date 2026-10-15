import sys
from pathlib import Path

from streamlit.web import cli as stcli


if getattr(sys, "frozen", False):
    app_path = Path(sys._MEIPASS) / "ign_sl.py"
else:
    app_path = Path(__file__).parent / "ign_sl.py"

sys.argv = [
    "streamlit",
    "run",
    str(app_path),
    "--server.fileWatcherType=none",
    "--global.developmentMode=false",
    "--server.port=8501",
    "--server.address=127.0.0.1",
    "--browser.gatherUsageStats=false",
]

stcli.main()