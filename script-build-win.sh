#!/bin/bash
. venv/Scripts/activate
cd build
python -m PyInstaller DataHub.spec --noconfirm