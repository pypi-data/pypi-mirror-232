import typing

from easyeda.core import _EasyEDAComponent
from easyeda.core.geometry import Point

"""
    # command: CA
    view box width: 2400(24000 mil), View Box Width / Canvas width = scaleX = 2
    view box height: 2400(24000 mil),View Box Height / Canvas Height = scaleY = 2
    back ground: #000000
    grid visible: yes/none
    grid color: #FFFFFF
    grid size: 10(100 mil)
    canvas width: 1200 (12000 mil)
    canvas height: 1200 (12000 mil)
    grid style: line/dot
    snap size: 1 (10 mil)
    unit: mil(inch, mil, mm)
    routing width: 1 (10mil)
    routing angle: 45 degree( 45 90 free)
    copper area: visible/invisible
    ALT snap size: 0.5 ( 5 mil Snap Size when pressing the ALT Key)
    origin x position
    origin y position
"""


class Canvas(_EasyEDAComponent):
    def __init__(
        self,
        unit="mil",
        width: int = 1200,
        height: int = 1200,
        origin=Point(0, 0),
        grid_size=10,
        grid_style="line",
        snap_size=1,
        alt_snap_size=0.5,
        routing_width=1,
        routing_angle=45,
        show_grid=True,
        show_copper_area=True,
        background_color: str = "#000000",
        grid_color="#FFFFFF",
    ):
        self.unit = unit
        self.vb_width = width * 2
        self.vb_height = height * 2
        self.width = width
        self.height = height
        self.origin = origin
        self.grid_size = grid_size
        self.grid_style = grid_style
        self.snap_size = snap_size
        self.alt_snap_size = alt_snap_size
        self.routing_width = routing_width
        self.routing_angle = routing_angle
        self.grid_visible = "yes" if show_grid else "none"
        self.copper_area = "visible" if show_copper_area else "invisible"
        self.background_color = background_color
        self.grid_color = grid_color

    def render(self) -> str:
        return "~".join(
            map(
                str,
                [
                    "CA",
                    self.vb_width,
                    self.vb_height,
                    self.background_color,
                    self.grid_visible,
                    self.grid_color,
                    self.grid_size,
                    self.width,
                    self.height,
                    self.grid_style,
                    self.snap_size,
                    self.unit,
                    self.routing_width,
                    self.routing_angle,
                    self.copper_area,
                    self.alt_snap_size,
                    self.origin.x,
                    self.origin.y,
                ],
            )
        )
