import logging

import ulauncher.utils.display as display
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

import monitor_helper as mh
from gnome_windows_client import GnomeWindowsExtensionClient

logger = logging.getLogger(__name__)


class WindowManagerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []

        # Add window management options
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Move Up",
                description="Move the focused window to the top edge of the screen",
                on_enter=ExtensionCustomAction({"action": "up"}),
            )
        )
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Move Down",
                description="Move the focused window to the bottom edge of the screen",
                on_enter=ExtensionCustomAction({"action": "down"}),
            )
        )
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Move Left",
                description="Move the focused window to the left edge of the screen",
                on_enter=ExtensionCustomAction({"action": "left"}),
            )
        )
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Move Right",
                description="Move the focused window to the right edge of the screen",
                on_enter=ExtensionCustomAction({"action": "right"}),
            )
        )
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Maximize",
                description="Maximize the focused window",
                on_enter=ExtensionCustomAction({"action": "maximize"}),
            )
        )
        items.append(
            ExtensionResultItem(
                icon="images/wm-logo.svg",
                name="Unmaximize",
                description="Unmaximize the focused window",
                on_enter=ExtensionCustomAction({"action": "unmaximize"}),
            )
        )

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        wm_action = data["action"]
        WindowManagerAction(wm_action)


def WindowManagerAction(wm_action):
    monitor = mh.get_monitor_of_focused_window(client)
    if monitor is None:
        logger.error("Failed to get monitor details")
        return

    # TODO: fix that!
    system_bar_height = 34

    wm_actions = {
        "left": (
            "move-resize",
            str(monitor.x),
            str(monitor.y + system_bar_height),
            str(monitor.width // 2),
            str(monitor.height - system_bar_height),
        ),
        "right": (
            "move-resize",
            str(monitor.x + (monitor.width // 2)),
            str(monitor.y + system_bar_height),
            str(monitor.width // 2),
            str(monitor.height - system_bar_height),
        ),
        "up": (
            "move-resize",
            str(monitor.x),
            str(monitor.y + system_bar_height),
            str(monitor.width),
            str((monitor.height - system_bar_height) // 2),
        ),
        "down": (
            "move-resize",
            str(monitor.x),
            str(
                monitor.y
                + system_bar_height
                + (monitor.height - system_bar_height) // 2
            ),
            str(monitor.width),
            str((monitor.height - system_bar_height) // 2),
        ),
        "maximize": ("maximize",),
        "unmaximize": ("unmaximize",),
    }

    if wm_action in wm_actions:
        selected_action = wm_actions[wm_action]

        focused_window_id = client.get_focused_window_id()
        if focused_window_id is None:
            logger.error("No focused window id found")
            return

        if selected_action[0] == "move-resize":
            # Extract action and coordinates from directions dictionary
            _, x, y, width, height = selected_action
            client.move_resize(
                focused_window_id, int(x), int(y), int(width), int(height)
            )
        elif selected_action[0] == "maximize":
            client.maximize(focused_window_id)
        elif selected_action[0] == "unmaximize":
            client.unmaximize(focused_window_id)


if __name__ == "__main__":
    client = GnomeWindowsExtensionClient()
    WindowManagerExtension().run()
