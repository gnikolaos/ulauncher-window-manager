import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional

import ulauncher.utils.display as display

from gnome_windows_client import GnomeWindowsExtensionClient


@dataclass
class Monitor:
    id: int
    x: int
    y: int
    width: int
    height: int
    isPrimary: bool


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
) -> Optional[Monitor]:
    focused_window_id = client.get_focused_window_id()
    if not focused_window_id:
        return None

    focused_window_monitor_id = client.get_window_details(focused_window_id).monitor
    if focused_window_monitor_id is None:
        return None

    active_monitors = get_active_monitors()

    for monitor in active_monitors:
        if monitor.id == focused_window_monitor_id:
            return monitor

    return None
