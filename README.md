# Trigger Detent

This tool maps analog joystick triggers to different keyboard keys based on how far you press them.

## Installation

Install `uv` by running this command in PowerShell:  
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`  
(this is for Windows PowerShell. Refer to the [official documentation](https://docs.astral.sh/uv/getting-started/installation/) for other environments.)

## Usage

Double-click `run.bat` to start. This will automatically set up everything and run the script.

## Configuration

Edit `config.ini` to change settings:
- **[keybind]**: Set the keys triggered by the first and second stage of the press.
- **[threshold]**: Set the points where the first and second stage activate (between -1.0 and 1.0).
- **[axis]**: Set the joystick axis numbers for your controller's triggers.

## Shout-out

This tool was made for @ysw1601 to play AH-64D in DCS World.