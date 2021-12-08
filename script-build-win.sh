#!/bin/bash
. venv/Scripts/activate
rm -rf __pycache__
cd build
rm -rf build
rm -rf dist
python -m PyInstaller DataHub.spec --noconfirm