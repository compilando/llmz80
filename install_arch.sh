#!/bin/bash

# Exit on error
set -e

# Check for AUR helper
if command -v yay &> /dev/null; then
    AUR_HELPER="yay"
elif command -v paru &> /dev/null; then
    AUR_HELPER="paru"
else
    echo "Error: Neither yay nor paru found. Please install an AUR helper first."
    echo "Install yay with:"
    echo "git clone https://aur.archlinux.org/yay.git"
    echo "cd yay"
    echo "makepkg -si"
    exit 1
fi

echo "Installing system dependencies..."
yay -S --needed \
    base-devel \
    fuse-emulator \
    python-pip \
    dialog

echo "Installing z88dk from AUR..."
$AUR_HELPER -S --needed z88dk-git

echo "Installing uv..."
# pip install -U uv

echo "Creating Python virtual environment and installing dependencies..."
uv venv
uv pip install -r requirements.txt

echo "Making build script executable..."
chmod +x build.sh

echo "Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your OpenAI API key"
fi

echo "Installation complete!"
echo "Remember to set your OpenAI API key in the .env file"
echo "Activate the virtual environment with:"
echo "source .venv/bin/activate"
