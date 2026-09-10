from os import getenv
from pathlib import Path


class Paths:
    ROOT = Path(__file__).resolve().parent.parent.parent

    GIGACHAT = ROOT / ".venv" / "Lib" / "site-packages" / "gigachat"
    MAXAPI = ROOT / ".venv" / "Lib" / "site-packages" / "maxapi"

    FONT = ROOT / "bot" / "assets" / "consola.ttf"
    CERTIFICATE = ROOT / "bot" / "assets" / "Russian_Trusted_Root_CA.cer"

    TESTS = ROOT / "backups" / "tests"

    SECRETS = Path(getenv("SECRETS") or ROOT / "secrets")
