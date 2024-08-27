import json
from dataclasses import dataclass
from typing import List, Optional, Type

from dbus import Interface, SessionBus


@dataclass
class Window:
    in_current_workspace: bool
    wm_class: str
    wm_class_instance: str
    pid: int
    id: int
    frame_type: int
    window_type: int
    focus: bool
    maximized: Optional[int] = None
    layer: Optional[int] = None
    monitor: Optional[int] = None
    role: Optional[str] = None
    title: Optional[str] = None
    canClose: Optional[bool] = None
    canMaximize: Optional[bool] = None
    canMinimize: Optional[bool] = None
    canMove: Optional[bool] = None
    canResize: Optional[bool] = None
    currentMonitorWorkArea: Optional[dict] = None
    allMonitorsWorkArea: Optional[dict] = None
    windowArea: Optional[dict] = None


@dataclass
class FrameRect:
    x: int
    y: int
    width: int
    height: int


class GnomeWindowsExtensionClient:
    def __init__(self):
        self.bus = SessionBus()
        self.proxy = self.bus.get_object(
            "org.gnome.Shell", "/org/gnome/Shell/Extensions/WindowCalls"
        )
        self.interface = Interface(
            self.proxy, dbus_interface="org.gnome.Shell.Extensions.WindowCalls"
        )

    def _parse_response_to_object(
        self, response: str, obj_type: Type[Window]
    ) -> List[Window]:
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return [obj_type(**item) for item in data]
            return [obj_type(**data)]
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing response: {e}")

    def list_windows(self) -> List[Window]:
        response = self.interface.List()
        return self._parse_response_to_object(response, Window)

    def get_window_details(self, winid: int) -> Window:
        response = self.interface.Details(winid)
        windows = self._parse_response_to_object(response, Window)
        return windows[0]

    def get_window_title(self, winid: int):
        return self.interface.GetTitle(winid)

    def get_frame_rect(self, winid: int) -> FrameRect:
        return self.interface.GetFrameRect(winid)

    def get_frame_bounds(self, winid: int):
        return self.interface.GetFrameBounds(winid)

    # Actions
    def move_to_workspace(self, winid: int, workspace_num: int):
        self.interface.MoveToWorkspace(winid, workspace_num)

    def place(self, winid: int, x: int, y: int, width: int, height: int):
        self.interface.Place(winid, x, y, width, height)

    def resize(self, winid: int, width: int, height: int):
        self.interface.Resize(winid, width, height)

    def move(self, winid: int, x: int, y: int):
        self.interface.Move(winid, x, y)

    def maximize(self, winid: int):
        self.interface.Maximize(winid)

    def minimize(self, winid: int):
        self.interface.Minimize(winid)

    def unmaximize(self, winid: int):
        self.interface.Unmaximize(winid)

    def unminimize(self, winid: int):
        self.interface.Unminimize(winid)

    def activate(self, winid: int):
        self.interface.Activate(winid)

    def close(self, winid: int):
        self.interface.Close(winid)

    # Composite actions
    def get_focused_window_id(self) -> Optional[int]:
        windows = self.list_windows()
        focused_window = next((window for window in windows if window.focus), None)
        if focused_window:
            return focused_window.id
        return None
