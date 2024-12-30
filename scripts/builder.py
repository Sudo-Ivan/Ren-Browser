import PyInstaller.__main__
import os
import sys


def build_api():
    PyInstaller.__main__.run(
        [
            "ren_api/main.py",
            "--onefile",
            "--name=ren-api",
            # Core dependencies
            "--hidden-import=uvicorn",
            "--hidden-import=fastapi",
            "--hidden-import=pydantic",
            "--hidden-import=msgpack",
            # RNS and LXMF dependencies
            "--hidden-import=lxmf",
            "--hidden-import=rns",
            "--hidden-import=RNS.Interface",
            "--hidden-import=RNS.Interfaces",
            "--hidden-import=RNS.Interfaces.Interface",
            "--hidden-import=RNS.Interfaces.LocalInterface",
            "--hidden-import=RNS.Interfaces.AutoInterface",
            "--hidden-import=RNS.Transport",
            "--hidden-import=RNS.Reticulum",
            "--hidden-import=RNS.Identity",
            "--hidden-import=RNS.Config",
            # Build paths
            "--distpath=dist",
            "--workpath=build",
            "--specpath=build",
            "--clean",
        ]
    )
