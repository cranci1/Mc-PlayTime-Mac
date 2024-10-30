import os
import gzip
from datetime import datetime
from pyfiglet import figlet_format
from rich import print
from rich.console import Console
from rich.table import Table
import concurrent.futures
from rich.progress import Progress, SpinnerColumn, TextColumn

def process_log_file(log_file_path, launcher_name):
    if launcher_name == "Bad Lion" and not log_file_path.endswith(".log"):
        print(f"[yellow]Skipping non-log file: {log_file_path}[/yellow]")
        return 0

    try:
        if log_file_path.endswith(".log.gz"):
            with gzip.open(log_file_path, 'rt') as gz_file:
                log_contents = gz_file.read()
        elif log_file_path.endswith(".log"):
            with open(log_file_path, 'rt') as log_file:
                log_contents = log_file.read()
        else:
            print(f"[red]Unsupported file format: {log_file_path}[/red]")
            return 0

        play_time_seconds = calculate_play_time(log_contents)
        formatted_play_time = format_play_time(play_time_seconds)
        print(f"Play time in {log_file_path}: {formatted_play_time}")
        return play_time_seconds
    except Exception as e:
        print(f"[red]Error processing {log_file_path}: {str(e)}[/red]")
        return 0

def calculate_play_time(log_contents):
    lines = log_contents.split('\n')
    start_time, end_time = None, None

    for line in lines:
        if '[' in line and ']' in line:
            try:
                time_str = line.split('[')[1].split(']')[0]
                time = datetime.strptime(time_str, '%H:%M:%S')
                if start_time is None:
                    start_time = time
                end_time = time
            except ValueError:
                continue

    if start_time and end_time:
        elapsed_time = end_time - start_time
        return int(elapsed_time.total_seconds())
    return 0

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
    console = Console()
    console.print("\n[bold cyan]Available Launchers:[/bold cyan]")
    launchers = [
        "Minecraft Launcher/TLauncher", "TLauncher-Legacy", "BadLion Client", "Lunar Client",
        "GDLauncher", "Prism Launcher", "MultiMc", "ATLauncher", "Modrinth", "CurseForge", "Custom Path"
    ]
    for idx, launcher in enumerate(launchers, 1):
        console.print(f"[cyan]{idx}.[/cyan] {launcher}")

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
        choice = console.input("\n[bold cyan]Choose The Launcher (1-11): [/bold cyan]")

        if choice in launcher_paths:
            if choice in ["5", "6", "7", "9", "10"]:
                instance_name = console.input("[bold cyan]Enter the Instance/Modpack name: [/bold cyan]")
                logs_directory = os.path.expanduser(launcher_paths[choice].format(instance_name))
                launcher_name = f"{launchers[int(choice)-1]}, {instance_name}"
            elif choice == "8":
                original_version = console.input("[bold cyan]Enter the version: [/bold cyan]").replace(".", "")
                console.print("\n[bold cyan]Choose the loader:[/bold cyan]")
                console.print("1. Vanilla\n2. Fabric\n3. Forge\n4. Legacy Fabric\n5. NeoForge\n6. Quilt")
                sub_choice = console.input("[bold cyan]Enter your choice (1-6): [/bold cyan]")
                loaders = ["Vanilla", "withFabric", "withForge", "withLegacyFabric", "withNeoForge", "withQuilt"]
                if sub_choice in map(str, range(1, 7)):
                    loader = loaders[int(sub_choice) - 1]
                    logs_directory = os.path.expanduser(f"/Applications/ATLauncher.app/Contents/Java/instances/Minecraft{original_version}{loader}/logs")
                    launcher_name = f"ATLauncher on {original_version} {loader}"
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")
                    continue
            else:
                logs_directory = os.path.expanduser(launcher_paths[choice])
                launcher_name = launchers[int(choice) - 1]
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
            continue

        if os.path.exists(logs_directory):
            return logs_directory, launcher_name
        else:
            console.print(f"[red]Directory not found: {logs_directory}[/red]")
            continue_anyway = console.input("[bold yellow]Directory not found. Continue anyway? (yes/no): [/bold yellow]")
            if continue_anyway.lower() == "yes":
                return logs_directory, launcher_name

def main():
    console = Console()

    while True:
        art = figlet_format('MC Playtime', font='slant')
        console.print(f"[bold cyan]{art}[/bold cyan]")

        logs_directory, launcher_name = choose_launcher()
        total_play_time = 0

        log_files = [f for f in os.listdir(logs_directory) 
                    if f.endswith((".log.gz", ".log"))]

        if not log_files:
            console.print("[yellow]No log files found in the selected directory.[/yellow]")
            continue_choice = console.input("[bold cyan]Do you want to check another launcher? (yes/no): [/bold cyan]")
            if continue_choice.lower() != "yes":
                break
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing log files...", total=len(log_files))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_file = {
                    executor.submit(process_log_file, os.path.join(logs_directory, filename), launcher_name): filename
                    for filename in log_files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        play_time_seconds = future.result()
                        total_play_time += play_time_seconds
                        progress.advance(task)
                    except Exception as e:
                        console.print(f"[red]Error processing {filename}: {str(e)}[/red]")

        formatted_total_play_time = format_play_time(total_play_time)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Launcher", style="dim", width=20)
        table.add_column("Total Play Time", style="dim", width=20)
        table.add_row(launcher_name, formatted_total_play_time)

        console.print("\n[bold green]Results:[/bold green]")
        console.print(table)

        continue_choice = console.input("\n[bold cyan]Do you want to check another launcher? (yes/no): [/bold cyan]")
        if continue_choice.lower() != "yes":
            break

if __name__ == "__main__":
    main()
