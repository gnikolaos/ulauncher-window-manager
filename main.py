import logging
import threading
from typing import Literal, Tuple, Union

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.event import KeywordQueryEvent

import monitor_helper as mh
from gnome_windows_client import (
    GnomeWindowsExtensionClient,
    WorkspaceAndMonitorDirection,
)

logger = logging.getLogger(__name__)

# Window Manager actions types
PlaceAction = Tuple[Literal["place"], int, int, int, int]
WorkspaceMove = Tuple[Literal["workspace-move"], WorkspaceAndMonitorDirection]
MonitorMove = Tuple[Literal["monitor-move"], WorkspaceAndMonitorDirection]
MaximizeAction = Tuple[Literal["maximize"]]
UnmaximizeAction = Tuple[Literal["unmaximize"]]
MinimizeAction = Tuple[Literal["minimize"]]
CloseAction = Tuple[Literal["close"], bool]
FullscreenAction = Tuple[Literal["fullscreen"]]

WindowAction = Union[
    PlaceAction,
    WorkspaceMove,
    MonitorMove,
    MaximizeAction,
    UnmaximizeAction,
    MinimizeAction,
    CloseAction,
    FullscreenAction,
]


class WindowManagerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()

        for action, kw in extension.preferences.items():
            if kw == keyword:
                hide_window_action = HideWindowAction()
                threading.Timer(0.01, WindowManagerAction, args=[action]).start()
                return hide_window_action


def WindowManagerAction(action):
    monitor_of_focused_window = mh.get_monitor_of_focused_window(client)
    if monitor_of_focused_window is None:
        logger.error("Cannot find the monitor of the focused window")
        return
    monitor_work_area = monitor_of_focused_window.workArea

    window_manager_actions: dict[str, WindowAction] = {
        "top-half": (
            "place",
            monitor_work_area.x,
            monitor_work_area.y,
            monitor_work_area.width,
            monitor_work_area.height // 2,
        ),
        "bottom-half": (
            "place",
            monitor_work_area.x,
            monitor_work_area.y + monitor_work_area.height // 2,
            monitor_work_area.width,
            monitor_work_area.height // 2,
        ),
        "left-half": (
            "place",
            monitor_work_area.x,
            monitor_work_area.y,
            monitor_work_area.width // 2,
            monitor_work_area.height,
        ),
        "right-half": (
            "place",
            monitor_work_area.x + monitor_work_area.width // 2,
            monitor_work_area.y,
            monitor_work_area.width // 2,
            monitor_work_area.height,
        ),
        "center": (
            "place",
            monitor_work_area.x + monitor_work_area.width // 4,
            monitor_work_area.y + monitor_work_area.height // 4,
            monitor_work_area.width // 2,
            monitor_work_area.height // 2,
        ),
        "center-half": (
            "place",
            monitor_work_area.x + monitor_work_area.width // 4,
            monitor_work_area.y,
            monitor_work_area.width // 2,
            monitor_work_area.height,
        ),
        "center-three-fourths": (
            "place",
            monitor_work_area.x + monitor_work_area.width // 8,
            monitor_work_area.y + int(monitor_work_area.height * 0.075),
            (monitor_work_area.width * 3) // 4,
            int(monitor_work_area.height * 0.85),
        ),
        "first-three-fourths": (
            "place",
            monitor_work_area.x,
            monitor_work_area.y,
            int(monitor_work_area.width * 0.75),
            monitor_work_area.height,
        ),
        "last-three-fourths": (
            "place",
            monitor_work_area.x + int(monitor_work_area.width * 0.25),
            monitor_work_area.y,
            int(monitor_work_area.width * 0.75),
            monitor_work_area.height,
        ),
        "first-fourth": (
            "place",
            monitor_work_area.x,
            monitor_work_area.y,
            int(monitor_work_area.width * 0.25),
            monitor_work_area.height,
        ),
        "last-fourth": (
            "place",
            monitor_work_area.x + int(monitor_work_area.width * 0.75),
            monitor_work_area.y,
            int(monitor_work_area.width * 0.25),
            monitor_work_area.height,
        ),
        "almost-maximize": (
            "place",
            monitor_work_area.x + int(monitor_work_area.width * 0.02),
            monitor_work_area.y + int(monitor_work_area.height * 0.02),
            int(monitor_work_area.width * 0.96),
            int(monitor_work_area.height * 0.96),
        ),
        "next-desktop": ("workspace-move", "right"),
        "previous-desktop": ("workspace-move", "left"),
        "right-monitor": ("monitor-move", "right"),
        "left-monitor": ("monitor-move", "left"),
        "maximize": ("maximize",),
        "unmaximize": ("unmaximize",),
        "minimize": ("minimize",),
        "fullscreen": ("fullscreen",),
        "close": ("close", False),
        "force-close": ("close", True),
    }

    if action in window_manager_actions:
        selected_action = window_manager_actions[action]

        focused_window_id = client.get_focused_window_id()
        if focused_window_id is None:
            logger.error("No focused window id found")
            return

        match selected_action[0]:
            case "place":
                # Extract action and coordinates from directions dictionary
                _, x, y, width, height = selected_action
                logger.info(
                    f"selected_action details: x:{x}, y:{y}, width:{width}, height:{height}"
                )
                client.place(focused_window_id, x, y, width, height)
            case "workspace-move":
                _, direction = selected_action
                client.move_to_workspace(focused_window_id, direction)
            case "monitor-move":
                _, direction = selected_action
                client.move_to_monitor(focused_window_id, direction)
            case "maximize":
                client.maximize(focused_window_id)
            case "unmaximize":
                client.unmaximize(focused_window_id)
            case "minimize":
                client.minimize(focused_window_id)
            case "close":
                _, is_forced = selected_action
                client.close(focused_window_id, is_forced)
            case "fullscreen":
                client.toggle_fullscreen(focused_window_id)


if __name__ == "__main__":
    client = GnomeWindowsExtensionClient()
    WindowManagerExtension().run()
