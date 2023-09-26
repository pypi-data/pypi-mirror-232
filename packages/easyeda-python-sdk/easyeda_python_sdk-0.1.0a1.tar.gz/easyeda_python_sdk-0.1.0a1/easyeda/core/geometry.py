import random
import typing

from easyeda.core import _EasyEDAComponent


class Point(_EasyEDAComponent):
    def __init__(self, x: float, y: float, unit="mil"):
        self.x = x
        self.y = y
        if unit == "mm":
            self.x = round(self.x * 3.937, 4)
            self.y = round(self.y * 3.937, 4)

    def as_complex(self):
        return complex(self.x, self.y)

    def render(self) -> str:
        return f"{self.x} {self.y * -1}"


class Hole:
    def __init__(self, center: Point, diameter: float, locked: bool):
        self.center = center
        self.diameter = diameter
        self.locked = locked


class Track(_EasyEDAComponent):
    def __init__(
        self,
        *points: Point,
        layer: int = 1,
        width: float = 1,
        net: str = "",
        id_: str = f"gge{random.randint(1500, 15000000)}",
        locked: bool = False,
    ):
        self.layer = layer
        self.width = width
        self.net = net
        self.id = id_
        self.locked = 1 if locked else 0

        self.points = points

    def render(self) -> str:
        points = " ".join([p.render() for p in self.points])
        return f"TRACK~{self.width}~{self.layer}~{self.net}~{points}~{self.id}~{self.locked}"


class Rectangle(_EasyEDAComponent):
    def __init__(
        self,
        width: float,
        height: float,
        layer: int = 1,
        center: Point = Point(0, 0),
        stroke_width: float = 10,
        unit="mil",
        net: str = "",
        id_: str = f"gge{random.randint(1500, 15000000)}",
        locked: bool = False,
    ):
        self.width = width if unit is "mil" else round(width * 3.937, 4)
        self.height = height if unit is "mil" else round(height * 3.937, 4)
        self.layer = layer
        self.center = center
        self.stroke_width = stroke_width if unit is "mil" else round(stroke_width * 3.937, 4)
        self.net = net
        self.id = id_
        self.locker = locked
