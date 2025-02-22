import os
import gzip
from datetime import datetime
from pyfiglet import Figlet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
import concurrent.futures
import time

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "red",
    "success": "green",
    "bold_cyan": "bold cyan",
    "bold_green": "bold green",
    "bold_yellow": "bold yellow",
    "bold_red": "bold red",
    "launcher": "bold magenta",
    "playtime": "bold blue",
    "directory": "dim white",
})

console = Console(theme=custom_theme)

def calculate_play_time(log_contents):
    start_time, end_time = None, None
    for line in log_contents.splitlines():
        if '[' in line and ']' in line:
            try:
                time_str = line.split('[')[1].split(']')[0]
                time = datetime.strptime(time_str, '%H:%M:%S').time()
                current_time = datetime.combine(datetime.today(), time)
                if start_time is None:
                    start_time = current_time
                end_time = current_time
            except ValueError:
                continue

    if start_time and end_time:
        elapsed_time = end_time - start_time
        return int(elapsed_time.total_seconds())
    return 0

def format_play_time(seconds):
    units = [("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    parts = []
    for unit, div in units:
        value = seconds // div
        if value:
            seconds %= div
            parts.append(f"{value} {unit}{'s' if value != 1 else ''}")
    return ", ".join(parts) or "0 seconds"

def process_log_file(log_file_path, launcher_name):
    try:
        if log_file_path.endswith(".log.gz"):
            with gzip.open(log_file_path, 'rt') as f:
                log_contents = f.read()
        elif log_file_path.endswith(".log"):
            with open(log_file_path, 'rt') as f:
                log_contents = f.read()
        else:
            console.print(f"[danger]Unsupported file: {log_file_path}[/danger]")
            return 0

        play_time = calculate_play_time(log_contents)
        console.print(f"  [playtime]>[/] {os.path.basename(log_file_path)}: [bold]{format_play_time(play_time)}[/]")
        return play_time
    except Exception as e:
        console.print(f"[danger]Error processing {log_file_path}: {e}[/danger]")
        return 0

def get_launcher_path(choice, launcher_paths):
    if choice in ["5", "6", "7", "9", "10"]:
        instance_name = console.input("[bold_cyan]Enter instance/modpack name:[/]")
        return os.path.expanduser(launcher_paths[choice].format(instance_name)), instance_name
    elif choice == "8":
        original_version = console.input("[bold_cyan]Enter version (e.g., 1.18.2):[/]").replace(".", "")
        console.print("\n[bold_cyan]Choose loader:[/]")
        console.print("1. Vanilla\n2. Fabric\n3. Forge\n4. Legacy Fabric\n5. NeoForge\n6. Quilt")
        sub_choice = console.input("[bold_cyan]Enter choice (1-6):[/]")
        loaders = ["Vanilla", "withFabric", "withForge", "withLegacyFabric", "withNeoForge", "withQuilt"]
        if sub_choice in map(str, range(1, 7)):
            loader = loaders[int(sub_choice) - 1]
            return os.path.expanduser(f"/Applications/ATLauncher.app/Contents/Java/instances/Minecraft{original_version}{loader}/logs"), f"ATLauncher {original_version} {loader}"
        else:
            console.print("[danger]Invalid loader choice.[/]")
            return None, None
    else:
        return os.path.expanduser(launcher_paths[choice]), None

def choose_launcher():
    console.print("\n[bold_cyan]Available Launchers:[/]")
    launchers = {
        "1": "Minecraft/TLauncher", "2": "TLauncher-Legacy", "3": "BadLion Client", "4": "Lunar Client",
        "5": "GDLauncher", "6": "Prism Launcher", "7": "MultiMc", "8": "ATLauncher", "9": "Modrinth",
        "10": "CurseForge", "11": "Custom Path"
    }
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

    for key, launcher in launchers.items():
        console.print(f"[info]{key}.[/] {launcher}")

    while True:
        choice = console.input("[bold_cyan]Choose launcher (1-11):[/]")
        if choice in launchers:
            logs_directory, instance_name = get_launcher_path(choice, launcher_paths)
            if logs_directory:
                launcher_name = f"{launchers[choice]}, {instance_name}" if instance_name else launchers[choice]
                if os.path.exists(logs_directory):
                    return logs_directory, launcher_name
                else:
                    console.print(f"[danger]Directory not found: {logs_directory}[/]")
                    if console.input("[bold_yellow]Continue anyway? (yes/no):[/]").lower() == "yes":
                        return logs_directory, launcher_name
            else:
                continue
        else:
            console.print("[danger]Invalid choice.[/]")

def main():
    console.clear()
    f = Figlet(font='slant')
    console.print(Panel(Text(f.renderText("MC Playtime"), justify="center", style="bold green")))

    while True:
        logs_directory, launcher_name = choose_launcher()
        log_files = [f for f in os.listdir(logs_directory) if f.endswith((".log.gz", ".log"))]

        if not log_files:
            console.print("[warning]No log files found.[/]")
            if console.input("[bold_cyan]Check another launcher? (yes/no):[/]").lower() != "yes":
                break
            continue

        total_play_time = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            task = progress.add_task("[info]Processing logs...", total=len(log_files))
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(process_log_file, os.path.join(logs_directory, log), launcher_name) for log in log_files]
                for future in concurrent.futures.as_completed(futures):
                    total_play_time += future.result()
                    progress.advance(task)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Launcher", style="launcher", width=30)
        table.add_column("Total Play Time", style="playtime", width=20)
        table.add_row(launcher_name, format_play_time(total_play_time))
        console.print(Panel(table, title="[bold green]Results[/]"))

        if console.input("[bold_cyan]Check another launcher? (yes/no):[/]").lower() != "yes":
            break

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()