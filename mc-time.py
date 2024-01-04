import os
from datetime import datetime, timedelta
import gzip
from pyfiglet import figlet_format
from rich import print
from rich.console import Console
from rich.table import Table

def process_log_file(log_file_path, launcher_name):
    if launcher_name == "Bad Lion" and not log_file_path.endswith(".log"):
        # Skip non-log files for Bad Lion Client
        print(f"Skipping non-log file: {log_file_path}")
        return 0

    if log_file_path.endswith(".log.gz"):
        with gzip.open(log_file_path, 'rt') as gz_file:
            # Extract the log contents from the compressed file
            log_contents = gz_file.read()
    elif log_file_path.endswith(".log"):
        with open(log_file_path, 'rt') as log_file:
            # Read the log contents from the uncompressed file
            log_contents = log_file.read()
    else:
        print(f"Unsupported file format: {log_file_path}")
        return 0

    try:
        # Parse the log file and calculate play time
        play_time_seconds = calculate_play_time(log_contents)

        # Print or store the play time as needed
        formatted_play_time = format_play_time(play_time_seconds)
        print(f"Play time in {log_file_path}: {formatted_play_time}")
        return play_time_seconds
    except ValueError as e:
        print(f"Error processing {log_file_path}: {e}")
        return 0  # Return 0 seconds in case of an error

def calculate_play_time(log_contents):
    lines = log_contents.split('\n')

    # Extract the start time from the first line
    start_time_str = lines[0].split('[')[1].split(']')[0]
    start_time = datetime.strptime(start_time_str, '%H:%M:%S')

    # Initialize end_time to be the start_time
    end_time = start_time

    for line in lines[1:]:
        if '[' in line and ']' in line:
            time_str = line.split('[')[1].split(']')[0]
            try:
                time = datetime.strptime(time_str, '%H:%M:%S')
                end_time = max(end_time, time)
            except ValueError:
                # Skip lines that do not match the expected time format
                pass

    # Calculate the play time by finding the difference between the first and last time stamps
    elapsed_time = end_time - start_time
    play_time_seconds = int(elapsed_time.total_seconds())  # Convert to seconds

    return play_time_seconds

def format_play_time(play_time_seconds):
    if play_time_seconds < 60:
        return f"{play_time_seconds} {'second' if play_time_seconds == 1 else 'seconds'}"
    elif play_time_seconds < 3600:  # 60 seconds * 60 minutes
        minutes = int(play_time_seconds / 60)
        seconds = play_time_seconds % 60
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds:02d} seconds"
    elif play_time_seconds < 86400:  # 60 seconds * 60 minutes * 24 hours
        hours = int(play_time_seconds / 3600)
        minutes = int((play_time_seconds % 3600) / 60)
        return f"{hours} {'hour' if hours == 1 else 'hours'} and {minutes} {'minute' if minutes == 1 else 'minutes'}"
    else:
        days = int(play_time_seconds / 86400)
        hours = int((play_time_seconds % 86400) / 3600)
        minutes = int((play_time_seconds % 3600) / 60)
        return f"{days} {'day' if days == 1 else 'days'} and {hours} {'hour' if hours == 1 else 'hours'} and {minutes} {'minute' if minutes == 1 else 'minutes'}"

def choose_launcher():
    print("Available Launchers:")
    print("1. Minecraft Launcher")
    print("2. TLauncher-Legacy")
    print("3. Bad Lion")
    print("4. Lunar Client")
    print("5. GDLauncher")
    print("6. Custom Path")

    while True:
        choice = input("Enter the corresponding number: ")

        if choice == "1":
            logs_directory = os.path.expanduser("~/Library/Application Support/minecraft/logs")
            launcher_name = "Minecraft Launcher"
        elif choice == "2":
            logs_directory = os.path.expanduser("~/Library/Application Support/tlauncher/legacy/logs")
            launcher_name = "TLauncher-Legacy"
        elif choice == "3":
            logs_directory = os.path.expanduser("~/Library/Application Support/minecraft/logs/blclient/minecraft/")
            launcher_name = "Bad Lion"
        elif choice == "4":
            logs_directory = os.path.expanduser("~/.lunarclient/offline/multiver/logs")
            launcher_name = "Lunar Client"
        elif choice == "5":
            sub_choice = input("Choose: 'fabric' (1), 'forge' (2) or 'vanilla' (3):")
            if sub_choice == '1':
                logs_directory = os.path.expanduser("~/Library/Application Support/gdlauncher_next/instances/Minecraft fabric/logs")
                launcher_name = "GDLauncher (fabric)"
            elif sub_choice == '2':
                logs_directory = os.path.expanduser("~/Library/Application Support/gdlauncher_next/instances/Minecraft forge/logs")
                launcher_name = "GDLauncher (forge)"
            elif sub_choice == '3':
                logs_directory = os.path.expanduser("~/Library/Application Support/gdlauncher_next/instances/Minecraft vanilla/logs")
                launcher_name = "GDLauncher (vanilla)"
            else:
                print("Invalid sub-choice. Please try again.")
                continue
        elif choice == "6":
            custom_path = input("Enter the path to the logs folder: ")
            logs_directory = os.path.join(custom_path, "logs")
            launcher_name = "Custom Path"
        else:
            print("Invalid choice. Please try again.")
            continue

        if os.path.exists(logs_directory):
            return logs_directory, launcher_name
        else:
            print(f"The logs directory for {launcher_name} does not exist. Please choose again.")
def main():
    console = Console()

    while True:

        art = figlet_format('MC Playtime', font='slant')
        console.print(art)

        logs_directory, launcher_name = choose_launcher()

        total_play_time = 0

        # Loop through all .log.gz files in the specified directory
        for filename in os.listdir(logs_directory):
            if filename.endswith(".log.gz") or (launcher_name == "Bad Lion" and filename.endswith(".log")):
                log_file_path = os.path.join(logs_directory, filename)
                play_time_seconds = process_log_file(log_file_path, launcher_name)
                total_play_time += play_time_seconds

        formatted_total_play_time = format_play_time(total_play_time)

        # Create a table to display the results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Launcher", style="dim", width=12)
        table.add_column("Total Play Time", style="dim", width=20)
        table.add_row(launcher_name, formatted_total_play_time)

        console.print(table)

        # Ask the user if they want to continue or exit
        continue_choice = console.input("[bold cyan]Do you want to check another launcher? (yes/no): [/bold cyan]")
        if continue_choice.lower() != "yes":
            break

if __name__ == "__main__":
    main()
