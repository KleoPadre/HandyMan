from setuptools import setup

APP = ["main.py"]
DATA_FILES = [
    ("resources", ["resources/icon.png"]),
]
OPTIONS = {
    "argv_emulation": True,
    "packages": ["PyQt6", "utils", "ui"],
    "includes": ["PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets"],
    "excludes": ["tkinter"],
    "iconfile": "resources/icon.png",
    "plist": {
        "CFBundleName": "HandyMan",
        "CFBundleDisplayName": "HandyMan",
        "CFBundleGetInfoString": "HandyMan",
        "CFBundleIdentifier": "com.kleopadre.handyman",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "NSHumanReadableCopyright": "Copyright © 2023, Your Name, All Rights Reserved",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    license="MIT License",  # Specify the license
)
