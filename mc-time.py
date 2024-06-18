import os
import gzip
from datetime import datetime
from pyfiglet import figlet_format
from rich import print
from rich.console import Console
from rich.table import Table

def process_log_file(log_file_path, launcher_name):
    if launcher_name == "Bad Lion" and not log_file_path.endswith(".log"):
        print(f"Skipping non-log file: {log_file_path}")
        return 0

    try:
        if log_file_path.endswith(".log.gz"):
            with gzip.open(log_file_path, 'rt') as gz_file:
                log_contents = gz_file.read()
        elif log_file_path.endswith(".log"):
            with open(log_file_path, 'rt') as log_file:
                log_contents = log_file.read()
        else:
            print(f"Unsupported file format: {log_file_path}")
            return 0

        play_time_seconds = calculate_play_time(log_contents)
        formatted_play_time = format_play_time(play_time_seconds)
        print(f"Play time in {log_file_path}: {formatted_play_time}")
        return play_time_seconds
    except Exception as e:
        print(f"Error processing {log_file_path}: {e}")
        return 0

def calculate_play_time(log_contents):
    lines = log_contents.split('\n')

    try:
        start_time_str = lines[0].split('[')[1].split(']')[0]
        start_time = datetime.strptime(start_time_str, '%H:%M:%S')
    except (IndexError, ValueError) as e:
        print(f"Error parsing start time: {e}")
        return 0

    end_time = start_time

    for line in lines[1:]:
        if '[' in line and ']' in line:
            try:
                time_str = line.split('[')[1].split(']')[0]
                time = datetime.strptime(time_str, '%H:%M:%S')
                end_time = max(end_time, time)
            except ValueError:
                continue

    elapsed_time = end_time - start_time
    return int(elapsed_time.total_seconds())

def format_play_time(play_time_seconds):
    if play_time_seconds < 60:
        return f"{play_time_seconds} {'second' if play_time_seconds == 1 else 'seconds'}"
    elif play_time_seconds < 3600:
        minutes = play_time_seconds // 60
        seconds = play_time_seconds % 60
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} and {seconds} seconds"
    elif play_time_seconds < 86400:
        hours = play_time_seconds // 3600
        minutes = (play_time_seconds % 3600) // 60
        return f"{hours} {'hour' if hours == 1 else 'hours'} and {minutes} {'minute' if minutes == 1 else 'minutes'}"
    else:
        days = play_time_seconds // 86400
        hours = (play_time_seconds % 86400) // 3600
        minutes = (play_time_seconds % 3600) // 60
        return f"{days} {'day' if days == 1 else 'days'}, {hours} {'hour' if hours == 1 else 'hours'}, and {minutes} {'minute' if minutes == 1 else 'minutes'}"

def choose_launcher():
    print("Available Launchers:")
    launchers = [
        "Minecraft Launcher/TLauncher", "TLauncher-Legacy", "BadLion Client", "Lunar Client",
        "GDLauncher", "Prism Launcher", "MultiMc", "ATLauncher", "Modrinth", "CurseForge", "Custom Path"
    ]
    for idx, launcher in enumerate(launchers, 1):
        print(f"{idx}. {launcher}")

    launcher_paths = {
        "1": "~/Library/Application Support/minecraft/logs",
        "2": "~/Library/Application Support/tlauncher/legacy/logs",
        "3": "~/Library/Application Support/minecraft/logs/blclient/minecraft/",
        "4": "~/.lunarclient/offline/multiver/logs",
        "5": "~/Library/Application Support/gdlauncher_next/instances/{}/logs",
        "6": "~/Library/Application Support/PrismLauncher/instances/{}/.minecraft/logs",
        "7": "/Applications/MultiMC.app/Data/instances/{}/.minecraft/logs/",
        "8": "/Applications/ATLauncher.app/Contents/Java/instances/Minecraft{}/logs",
        "9": "~/Library/Application Support/com.modrinth.theseus/profiles/{}/logs",
        "10": "~/Documents/curseforge/minecraft/Instances/{}/logs",
        "11": "{}/logs"
    }

    while True:
        choice = input("Choose The Launcher: ")

        if choice in launcher_paths:
            if choice in ["5", "6", "7", "9", "10"]:
                instance_name = input("Enter the Instance/Modpack name: ")
                logs_directory = os.path.expanduser(launcher_paths[choice].format(instance_name))
                launcher_name = f"{launchers[int(choice)-1]}, {instance_name}"
            elif choice == "8":
                original_version = input("Enter the version: ").replace(".", "")
                sub_choice = input("1. Vanilla\n2. Fabric\n3. Forge\n4. Legacy Fabric\n5. NeoForge\n6. Quilt\nChoose the loader: ")
                loaders = ["Vanilla", "withFabric", "withForge", "withLegacyFabric", "withNeoForge", "withQuilt"]
                if sub_choice in map(str, range(1, 7)):
                    loader = loaders[int(sub_choice) - 1]
                    logs_directory = os.path.expanduser(f"/Applications/ATLauncher.app/Contents/Java/instances/Minecraft{original_version}{loader}/logs")
                    launcher_name = f"ATLauncher on {original_version} {loader}"
                else:
                    print("Invalid sub-choice. Please try again.")
                    continue
            else:
                logs_directory = os.path.expanduser(launcher_paths[choice])
                launcher_name = launchers[int(choice) - 1]
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

        for filename in os.listdir(logs_directory):
            if filename.endswith(".log.gz") or (launcher_name in ["CurseForge", "BadLion Client", "ATLauncher"] and filename.endswith(".log")):
                log_file_path = os.path.join(logs_directory, filename)
                play_time_seconds = process_log_file(log_file_path, launcher_name)
                total_play_time += play_time_seconds

        formatted_total_play_time = format_play_time(total_play_time)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Launcher", style="dim", width=20)
        table.add_column("Total Play Time", style="dim", width=20)
        table.add_row(launcher_name, formatted_total_play_time)

        console.print(table)

        continue_choice = console.input("[bold cyan]Do you want to check another launcher? (yes/no): [/bold cyan]")
        if continue_choice.lower() != "yes":
            break

if __name__ == "__main__":
    main()
