import datetime
import typing
from enum import Enum

import svg.path as _SVG

from easyeda.core.geometry import Point


class LayerType(Enum):
    SIGNAL = "Signal"
    NON_SIGNAL = "Non-Signal"
    PLANE = "Plane"
    OTHER = "Other"


class Layer:
    _pcb = None

    def __init__(self, id_: int, name: str, color: str, visible: bool, active: bool, config: bool):
        self.id = id_
        self.name = name
        self.color = color
        self.visible = "true" if visible else "false"
        self.active = "true" if active else "false"
        self.config = "true" if config else "false"
        self.layer_type = ""

    def add_lines(self, *points: Point, net: str = "", width: float = 10.0, locked: bool = False):
        points = " ".join([f"{o.x / 10} {o.y / 10 * -1}" for o in points])
        id_ = f"gge{datetime.datetime.now().timestamp()}".replace(".", "")
        locked = 1 if locked else 0
        self._pcb.shapes.append(f"TRACK~{width / 10}~{self.id}~{net}~{points}~{id_}~{locked}")

    def add_arc(
            self,
            start: Point,
            end: Point,
            radius: typing.Union[float, complex],
            net: str = "",
            width: float = 10,
            locked: bool = False,
    ):
        if not isinstance(radius, complex):
            radius = complex(radius, radius)

        radius = radius / 10
        locked = 1 if locked else 0
        width = width / 10.0

        start.x = start.x / 10
        start.y = start.y / 10 * -1

        end.x = end.x / 10
        end.y = end.y / 10 * -1

        path = _SVG.Path(_SVG.Move(start.as_complex()))
        id_ = f"gge{datetime.datetime.now().timestamp()}".replace(".", "")
        path.append(
            _SVG.Arc(start=start.as_complex(), radius=radius, rotation=0, arc=False, sweep=False, end=end.as_complex())
        )
        self._pcb.shapes.append(f"ARC~{width}~{self.id}~{net}~{path.d().replace(',', ' ')}~{id_}~{locked}")

    def add_rectangle(
            self,
            width: float,
            height: float,
            net: str,
            stroke_width: float = 10.0,
            center: Point = Point(0, 0),
            locked: bool = False,
            corner_radius: float = 0,
    ):
        center_x = center.x / 10
        center_y = center.y / 10 * -1

        if corner_radius > 0:
            points = [
                Point(center_x - width / 2.0 + corner_radius, center_y + height / 2.0),  # 1
                Point(center_x + width / 2.0 - corner_radius, center_y + height / 2.0),  # 2
                Point(center_x + width / 2.0, center_y + height / 2.0 - corner_radius),  # 3
                Point(center_x + width / 2.0, center_y - height / 2.0 + corner_radius),  # 4
                Point(center_x + width / 2.0 - corner_radius, center_y - height / 2.0),  # 5
                Point(center_x - width / 2.0 + corner_radius, center_y - height / 2.0),  # 6
                Point(center_x - width / 2.0, center_y - height / 2.0 + corner_radius),  # 7
                Point(center_x - width / 2.0, center_y + height / 2.0 - corner_radius),  # 8
            ]
            for i in range(0, len(points) - 1, 2):
                self.add_lines(*[points[i], points[i + 1]], width=stroke_width, locked=locked, net=net)
            for i in range(len(points) - 2, -1, -2):
                self.add_arc(points[i], points[i - 1], radius=corner_radius, width=stroke_width, locked=locked, net=net)
        else:
            points = [
                Point(center_x - width / 2.0, center_y + height / 2.0),
                Point(center_x + width / 2.0, center_y + height / 2.0),
                Point(center_x + width / 2.0, center_y - height / 2.0),
                Point(center_x - width / 2.0, center_y - height / 2.0),
                Point(center_x - width / 2.0, center_y + height / 2.0),
            ]
            self.add_lines(*points, width=stroke_width, locked=locked)

    def add_text(self, text: str, position: Point = Point(0, 0), font_size: float = 80.0, font_width: float = 8.0):
        font_size = font_size / 10
        font_width = font_width / 10
        pos_x = position.x / 10
        pos_y = position.y / 10 * -1
        self._pcb.shapes.append(
            f"TEXT~L~{pos_x}~{pos_y}~{font_width}~0~none~{self.id}~~{font_size}~{text}~"
        )

    def render(self):
        return f"{self.id}~{self.name}~{self.color}~{self.visible}~{self.active}~{self.config}~{self.layer_type}"


class BoardOutlineLayer(Layer):
    def add_lines(self, *points: Point, width: float = 10.0, locked: bool = False, net: str = ""):
        super(BoardOutlineLayer, self).add_lines(*points, net="", width=width, locked=locked)

    def add_rectangle(
            self,
            width: float,
            height: float,
            stroke_width: float = 10.0,
            center: Point = Point(0, 0),
            corner_radius: float = 0.0,
            locked: bool = False,
            net: str = "",
    ):
        super(BoardOutlineLayer, self).add_rectangle(
            width=width,
            height=height,
            net="",
            stroke_width=stroke_width,
            center=center,
            locked=locked,
            corner_radius=corner_radius,
        )

    def add_arc(
            self,
            start: Point,
            end: Point,
            radius: typing.Union[float, complex],
            width: float = 10,
            locked: bool = False,
            net: str = "",
    ):
        super(BoardOutlineLayer, self).add_arc(start, end, radius, net="", width=width, locked=locked)


class InnerCopperLayer(Layer):
    def set_layer_type(self, layer_type: LayerType):
        if layer_type.value in ["Signal", "Plane"]:
            self.layer_type = layer_type.value
        else:
            raise ValueError(
                f"Cannot set layer type '{layer_type.value}' for inner copper layer.\n" f"'Signal' or 'Plane' expected."
            )
