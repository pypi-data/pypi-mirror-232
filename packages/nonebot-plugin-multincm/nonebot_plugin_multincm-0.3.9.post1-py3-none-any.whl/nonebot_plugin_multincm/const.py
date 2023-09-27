from pathlib import Path

DATA_PATH = Path().cwd() / "data" / "multincm"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

RES_DIR = Path(__file__).parent / "res"
