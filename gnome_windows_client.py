import json
from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar, Union

from dbus import Interface, SessionBus


T = TypeVar("T")


@dataclass
class MtkRect:
    x: int
    y: int
    width: int
    height: int


@dataclass
class Window:
    id: int
    monitor: int
    wm_class: str
    wm_class_instance: str
    maximized: int
    focus: bool
    canMove: bool
    canResize: bool
    canClose: bool
    canMaximize: bool
    canMinimize: bool
    windowArea: MtkRect
    currentMonitorWorkArea: MtkRect
    allMonitorsWorkArea: MtkRect
    in_current_workspace: bool


@dataclass
class PartialWindow:
    id: int
    monitor: int
    focus: bool
    in_current_workspace: bool


@dataclass
class FocusedMonitorDetails:
    id: int
    geometry: MtkRect


class GnomeWindowsExtensionClient:
    def __init__(self):
        self.bus = SessionBus()
        self.proxy = self.bus.get_object(
            "org.gnome.Shell", "/org/gnome/Shell/Extensions/WindowCalls"
        )
        self.interface = Interface(
            self.proxy, dbus_interface="org.gnome.Shell.Extensions.WindowCalls"
        )

    def _parse_response_to_object(self, response: str, obj_type: Type[T]) -> List[T]:
        def parse_rects(data: dict):
            rect_fields = [
                "windowArea",
                "currentMonitorWorkArea",
                "allMonitorsWorkArea",
                "geometry",
            ]
            for field in rect_fields:
                if field in data and data[field] is not None:
                    data[field] = MtkRect(**data[field])

        try:
            data = json.loads(response)
            if isinstance(data, list):
                objects = []
                for item in data:
                    parse_rects(item)
                    objects.append(obj_type(**item))
                return objects

            # Handle single object
            parse_rects(data)
            return [obj_type(**data)]

        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing response: {e}")

    def list_windows(self) -> List[PartialWindow]:
        response = self.interface.List()
        return self._parse_response_to_object(response, PartialWindow)

    def get_window_details(self, winid: int) -> Window:
        response = self.interface.Details(winid)
        windows = self._parse_response_to_object(response, Window)
        return windows[0]

    def get_focused_monitor_details(self) -> FocusedMonitorDetails:
        response = self.interface.GetFocusedMonitorDetails()
        return self._parse_response_to_object(response, FocusedMonitorDetails)[0]

    # Actions
    def move_to_workspace(self, winid: int, workspace_num: int):
        self.interface.MoveToWorkspace(winid, workspace_num)

    def place(self, winid: int, x: int, y: int, width: int, height: int):
        self.interface.Place(winid, x, y, width, height)

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
        if focused_window is None:
            return None

        return focused_window.id
