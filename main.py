import logging
import threading
from typing import Literal, Tuple, Union

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.event import KeywordQueryEvent

import monitor_helper as mh
from gnome_windows_client import GnomeWindowsExtensionClient

logger = logging.getLogger(__name__)

# Window Manager actions types
PlaceAction = Tuple[Literal["place"], int, int, int, int]
MaximizeAction = Tuple[Literal["maximize"]]
UnmaximizeAction = Tuple[Literal["unmaximize"]]
CloseAction = Tuple[Literal["close"]]

WindowAction = Union[PlaceAction, MaximizeAction, UnmaximizeAction, CloseAction]


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
    monitor = mh.get_monitor_of_focused_window(client)
    if monitor is None:
        logger.error("Failed to get monitor details")
        return

    system_bar_height = mh.get_system_bar_height()

    window_manager_actions: dict[str, WindowAction] = {
        "top-half": (
            "place",
            monitor.x,
            monitor.y + system_bar_height,
            monitor.width,
            (monitor.height - system_bar_height) // 2,
        ),
        "bottom-half": (
            "place",
            monitor.x,
            monitor.y + system_bar_height + (monitor.height - system_bar_height) // 2,
            monitor.width,
            (monitor.height - system_bar_height) // 2,
        ),
        "left-half": (
            "place",
            monitor.x,
            monitor.y + system_bar_height,
            monitor.width // 2,
            monitor.height - system_bar_height,
        ),
        "right-half": (
            "place",
            monitor.x + monitor.width // 2,
            monitor.y + system_bar_height,
            monitor.width // 2,
            monitor.height - system_bar_height,
        ),
        "center": (
            "place",
            monitor.x + monitor.width // 4,
            monitor.y
            + int(system_bar_height + (monitor.height - system_bar_height) * 0.075),
            monitor.width // 2,
            int((monitor.height - system_bar_height) * 0.85),
        ),
        "center-half": (
            "place",
            monitor.x + monitor.width // 4,
            monitor.y + system_bar_height,
            monitor.width // 2,
            monitor.height - system_bar_height,
        ),
        "center-three-fourths": (
            "place",
            monitor.x + monitor.width // 8,
            monitor.y
            + int(system_bar_height + (monitor.height - system_bar_height) * 0.075),
            (monitor.width * 3) // 4,
            int((monitor.height - system_bar_height) * 0.85),
        ),
        "first-three-fourths": (
            "place",
            monitor.x,
            monitor.y + system_bar_height,
            int(monitor.width * 0.75),
            monitor.height - system_bar_height,
        ),
        "last-three-fourths": (
            "place",
            monitor.x + int(monitor.width * 0.25),
            monitor.y + system_bar_height,
            int(monitor.width * 0.75),
            monitor.height - system_bar_height,
        ),
        "first-fourth": (
            "place",
            monitor.x,
            monitor.y + system_bar_height,
            int(monitor.width * 0.25),
            monitor.height - system_bar_height,
        ),
        "last-fourth": (
            "place",
            monitor.x + int(monitor.width * 0.75),
            monitor.y + system_bar_height,
            int(monitor.width * 0.25),
            monitor.height - system_bar_height,
        ),
        "almost-maximize": (
            "place",
            monitor.x + int(monitor.width * 0.02),
            monitor.y
            + system_bar_height
            + int((monitor.height - system_bar_height) * 0.02),
            int(monitor.width * 0.96),
            int((monitor.height - system_bar_height) * 0.96),
        ),
        "maximize": ("maximize",),
        "unmaximize": ("unmaximize",),
        "close": ("close",),
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
            case "maximize":
                client.maximize(focused_window_id)
            case "unmaximize":
                client.unmaximize(focused_window_id)
            case "close":
                client.close(focused_window_id)
            case _:
                logger.error("Invalid action")


if __name__ == "__main__":
    client = GnomeWindowsExtensionClient()
    WindowManagerExtension().run()
