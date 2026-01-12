import sys
import os
import configparser
import time
import pygame

# --- Setup Paths ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.ini')


def load_config_values():
    """
    Load specific configuration values using ConfigParser for reading logic.
    Returns a default dict structure if file is missing/broken, or the loaded values.
    """
    defaults = {
        'calibration': {'ct_name': 'none'},
        'axis': {'ltaxis': '4', 'rtaxis': '5'}  # Default fallbacks
    }
    
    if not os.path.exists(CONFIG_FILE_PATH):
        return defaults

    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE_PATH, encoding='utf-8')
        
        # safely extract values or use defaults
        ct_name = config.get('calibration', 'ct_name', fallback='none')
        ltaxis = config.get('axis', 'ltaxis', fallback='4')
        rtaxis = config.get('axis', 'rtaxis', fallback='5')
        
        return {
            'calibration': {'ct_name': ct_name},
            'axis': {'ltaxis': ltaxis, 'rtaxis': rtaxis}
        }
    except Exception as e:
        print(f"Warning: Could not read config file ({e}). Using defaults.")
        return defaults


def update_ini_line(lines, section, key, value):
    """
    Helper to update or add a key=value pair in a specific section within a list of lines.
    Returns the modified list of lines.
    """
    section_found = False
    key_found = False
    in_correct_section = False
    new_lines = []
    
    # Normalize section header for search
    target_section_header = f"[{section}]"
    
    # Iterate to find section and key
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check for section change
        if stripped.startswith('[') and stripped.endswith(']'):
            if stripped == target_section_header:
                in_correct_section = True
                section_found = True
            else:
                if in_correct_section and not key_found:
                    # We are leaving the target section and haven't found the key yet.
                    # Insert the key before the new section starts.
                    new_lines.append(f"{key} = {value}\n")
                    key_found = True # Handled
                in_correct_section = False
        
        # Check for key if we are in the correct section
        if in_correct_section and not key_found:
            # Ignore comments and invalid lines
            if '=' in line and not stripped.startswith(';'):
                current_key = line.split('=', 1)[0].strip()
                if current_key == key:
                    # Found the key, replace the line
                    new_lines.append(f"{key} = {value}\n")
                    key_found = True
                    continue 

        new_lines.append(line)
        
    # If we reached the end of the file
    if not section_found:
        # Append section and key at the end
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        new_lines.append(f"\n{target_section_header}\n")
        new_lines.append(f"{key} = {value}\n")
    elif section_found and not key_found:
        # Section existed but key was not found by the time we finished the file
        # Append key at the very end (safe assumption as we are technically still "after" that section)
        # However, to be cleaner, we might want to check if the last line is blank
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        new_lines.append(f"{key} = {value}\n")

    return new_lines


def save_config_updates(updates):
    """
    Read config file as text, apply updates, and write back to preserve comments.
    updates: dict {section: {key: value}}
    """
    try:
        # Read existing file or start empty
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []

        # Apply updates sequentially
        for section, settings in updates.items():
            for key, val in settings.items():
                lines = update_ini_line(lines, section, key, val)

        # Write back
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Configuration saved successfully.")
        
    except Exception as e:
        print(f"Error saving config file: {e}")


def wait_for_controller():
    """Wait until exactly one controller is connected."""
    print("Scanning for controllers...")
    while True:
        pygame.event.pump()
        joysticks = pygame.joystick.get_count()

        if joysticks == 0:
            print("No controllers detected. Please connect your device...", end='\r')
        elif joysticks > 1:
            print(f"{joysticks} controllers detected. Please disconnect others...", end='\r')
        else:
            print("\nController detected!")
            # Initialize the single connected joystick
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                return joystick
            except pygame.error as e:
                print(f"\nError initializing joystick: {e}")
        
        time.sleep(1)


def detect_axis(joystick, axis_name):
    """Wait for user to press a specific axis (trigger) and return its index."""
    print(f"\nPlease press the {axis_name} only.")
    
    # Wait for the user to potentially release previous input
    time.sleep(1)
    pygame.event.clear()

    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Use a threshold (e.g., 0.5) to avoid detecting slight stick drift
                if abs(event.value) > 0.5:
                    print(f"Input detected on Axis {event.axis} (Value: {event.value:.2f})")
                    return event.axis
        
        # Small sleep to prevent high CPU usage
        time.sleep(0.01)


def main():
    pygame.init()
    
    print("--- Controller Calibration Tool ---")
    
    # Check if config exists, just to warn user if it's missing (created later)
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Warning: {CONFIG_FILE_PATH} not found. A new one will be created.")

    print("Please disconnect all other controllers except the one you want to calibrate.")
    input("Press Enter to start...")

    joystick = wait_for_controller()
    
    controller_name = joystick.get_name()
    print(f"Identified Controller: {controller_name}")
    
    # Prepare the updates dictionary
    updates = {
        'calibration': {'ct_name': f'"{controller_name}"'}, # Quote string for INI safety if needed
        'axis': {}
    }

    # Detect Left Trigger
    lt_axis = detect_axis(joystick, "LEFT TRIGGER")
    updates['axis']['ltaxis'] = str(lt_axis)
    print(f"Left Trigger saved as Axis {lt_axis}")

    # Detect Right Trigger
    rt_axis = detect_axis(joystick, "RIGHT TRIGGER")
    updates['axis']['rtaxis'] = str(rt_axis)
    print(f"Right Trigger saved as Axis {rt_axis}")

    print("\nCalibration complete.")
    save_config_updates(updates)
    
    input("Press Enter to exit...")
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()