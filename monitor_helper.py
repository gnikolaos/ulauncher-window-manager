import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional

import ulauncher.utils.display as display

from gnome_windows_client import GnomeWindowsExtensionClient, MtkRect


@dataclass
class Monitor:
    id: int
    x: int
    y: int
    width: int
    height: int
    isPrimary: bool


@dataclass
class MonitorOfFocusedWindow:
    id: int
    workArea: MtkRect


def get_active_monitors() -> List[Monitor]:
    # Run xrandr command and capture output
    result = subprocess.run(
        ["xrandr", "--listactivemonitors"], capture_output=True, text=True
    )
    output = result.stdout

    # Extract monitor details
    pattern = r"(\d+): (\+\S+?) (\d+)\/\d+x(\d+)\/\d+"
    matches = re.findall(pattern, output)
    monitors: list[Monitor] = []
    for match in matches:
        id, identifier, width, height = match
        isPrimary = True if "*" in identifier else False
        screen_geometry = display.get_screens()[int(id)]
        monitors.append(
            Monitor(
                int(id),
                int(screen_geometry["x"]),
                int(screen_geometry["y"]),
                int(width),
                int(height),
                isPrimary,
            )
        )

    return monitors


def get_monitor_of_focused_window(
    client: GnomeWindowsExtensionClient,
) -> Optional[MonitorOfFocusedWindow]:
    focused_window_id = client.get_focused_window_id()
    if not focused_window_id:
        return None

    focused_window_details = client.get_window_details(focused_window_id)
    id = focused_window_details.monitor
    workArea = focused_window_details.currentMonitorWorkArea

    return MonitorOfFocusedWindow(id, workArea)


def get_system_bar_height() -> int:
    try:
        # Run xprop command and capture output
        result = subprocess.run(
            ["xprop", "-root", "_NET_WORKAREA"], capture_output=True, text=True
        )
        output = result.stdout

        # Extract system bar height using regex
        match = re.search(
            r"_NET_WORKAREA\(CARDINAL\) = (\d+), (\d+), (\d+), (\d+)", output
        )
        if match:
            top_edge = int(match.group(2))
            return top_edge
        else:
            raise ValueError("Could not determine system bar height from xprop output")

    except subprocess.CalledProcessError:
        return 48  # Return a default value if the command fails
