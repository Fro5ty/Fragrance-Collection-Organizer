#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Fragrance Collection Organizer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Build script for creating a standalone executable using PyInstaller
"""

import os
import subprocess
import sys
import shutil
import re


def main():
    """Execute PyInstaller to build the executable"""
    print("Building Fragrance Collection Organizer...")

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Delete any existing spec file to ensure clean build
    spec_file = "Fragrance Organizer.spec"
    if os.path.exists(spec_file):
        print(f"Removing existing spec file: {spec_file}")
        os.remove(spec_file)

    spec_args = [
        "main.py",
        "--name=Fragrance Organizer",
        "--windowed",
        "--icon=src/resources/icon.ico",
        "--onefile",
        "--clean",
        "--add-data=fragrances.db;.",
        "--add-data=src/resources/icon.ico;.",
    ]

    print("Creating executable with PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller"] + spec_args)

    print("\nBuild completed successfully!")
    print("The executable can be found in the 'dist' folder.")


if __name__ == "__main__":
    main() 