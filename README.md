# Trigger Detent

This tool maps analog joystick triggers to different keyboard keys based on how far you press them.

## Installation

### For End Users (Executable)

1. Download the latest release `.zip` file.
2. Extract the contents to a folder of your choice.
3. Keep `TriggerDetent.exe`, `Calibrate.exe`, and `config.ini` in the same folder.
4. DO NOT DELETE _internal/ folder.

### For Developers (Source Code)

1. Install `uv` (refer to [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)).
2. Clone this repository.
3. Run `uv sync` to install dependencies.
4. uv sync may fail due to the lack of provided binaries for pygame and pydirectinput for some environments. Troubleshooting may be required.
5. To build executable, `uv run pyinstaller --noconfirm --onedir --clean --name [Calibrate/TriggerDetent] --add-data "config.ini;." [calibrate.py/main.py]`

## Usage

### Setup and Calibration

Before using the tool for the first time or if you change controllers:

1. Connect your controller.
2. Run `Calibrate.exe` (or `uv run calibrate.py` if running from source).
3. Follow the on-screen prompts to identify your controller and triggers.
   - This updates `config.ini` with your device name and axis numbers.

### Running the Tool

1. Run `TriggerDetent.exe` (or `run.bat` / `uv run main.py`).
2. Play your game while keeping the window open.
3. The tool will listen for trigger inputs and simulate key presses according to your configuration.

## Configuration

Edit `config.ini` to change specific settings if needed:

- **[keybind]**: Set the keys triggered by the first and second stage of the press.
- **[threshold]**: Set the values (-1.0 to 1.0) where the first and second stage activate.
- **[axis]**: Managed by the Calibrate tool. Axis numbers for triggers.
- **[calibration]**: Managed by the Calibrate tool. Stores the specific controller name to filter inputs.

## Shout-out

This tool was made for @ysw1601 to play AH-64D in DCS World.

## To Do

- 1st detent is getting properly recognized as hold, but 2nd detent is recognized as single input by DCS. Fix needed.