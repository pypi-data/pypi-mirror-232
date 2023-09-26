import os
from typing import Optional
from pathlib import Path


def fpath(__path: str):
    if not os.path.exists(__path):
        basename = os.path.basename(__path)
        if "." in basename:
            dirname = os.path.dirname(__path)
            os.makedirs(dirname, exist_ok=True)
    return __path


def remove_path(__path: Path):
    if __path.exists():
        os.remove(__path)


def filename(__path: str):
    return os.path.basename(__path)


def get_dirpaths(__path: Path or str, ext: str):
    if not ext.startswith("."):
        ext = f".{ext}"
    result = [file.path for file in os.scandir(__path) if file.path.endswith(ext)]
    return result


def get_save_dir(
    save_dir: Optional[str or Path],
    default_save_dir: str,
    root_dir: Optional[str] = None,
):
    if save_dir is None:
        if root_dir is None:
            root_dir = os.getcwd()
        save_dir = os.path.join(root_dir, default_save_dir)
    os.makedirs(save_dir, exist_ok=True)
    if not isinstance(save_dir, Path):
        save_dir = Path(save_dir)
    return save_dir
