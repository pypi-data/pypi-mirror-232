from rich.console import Console

console = Console()


def get_logo() -> str:
    return r"""
______                 _____             _   _  __       
| ___ \               /  ___|           | | (_)/ _|      
| |_/ /___  ___ ______\ `--. _ __   ___ | |_ _| |_ _   _ 
|    // _ \/ __|______|`--. \ '_ \ / _ \| __| |  _| | | |
| |\ \  __/ (__       /\__/ / |_) | (_) | |_| | | | |_| |
\_| \_\___|\___|      \____/| .__/ \___/ \__|_|_|  \__, |
                            | |                     __/ |
                            |_|                    |___/ 
"""


def clear_lines(n: int) -> None:
    """
    Clears the specified number of lines in the console.
    """
    for i in range(n):
        print("\033[1A", end="\x1b[2K")
