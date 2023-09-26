import datetime
import json
import random

from easyeda.core import DocumentType
from easyeda.core.canvas import Canvas
from easyeda.core.geometry import Point
from easyeda.core.layers import Layer, BoardOutlineLayer, InnerCopperLayer


class PCB:
    document_type = DocumentType.PCB
    TOP_LAYER: Layer = None
    BOTTOM_LAYER: Layer = None
    TOP_SILK_LAYER: Layer = None
    BOTTOM_SILK_LAYER: Layer = None
    TOP_PASTER_LAYER: Layer = None
    BOTTOM_PASTER_LAYER: Layer = None
    TOP_SOLDER_LAYER: Layer = None
    BOTTOM_SOLDER_LAYER: Layer = None
    RAT_LINES_LAYER: Layer = None
    BOARD_OUTLINE_LAYER: BoardOutlineLayer = None
    MULTI_LAYER_LAYER: Layer = None
    DOCUMENT_LAYER: Layer = None
    INNER_1_LAYER: InnerCopperLayer = None
    INNER_2_LAYER: InnerCopperLayer = None

    def __init__(self, version="1.0.0", canvas: Canvas = Canvas(), copper_layers: int = 2):
        self.version = version
        self.canvas = canvas
        self.TOP_LAYER = Layer(1, "TopLayer", "#FF0000", True, True, True)
        self.BOTTOM_LAYER = Layer(2, "BottomLayer", "#0000FF", True, False, True)
        self.TOP_SILK_LAYER = Layer(3, "TopSilkLayer", "#FFFF00", True, False, True)
        self.BOTTOM_SILK_LAYER = Layer(4, "BottomSilkLayer", "#808000", True, False, True)
        self.TOP_PASTER_LAYER = Layer(5, "TopPasterLayer", "#808080", True, False, False)
        self.BOTTOM_PASTER_LAYER = Layer(6, "BottomPasterLayer", "#800000", True, False, False)
        self.TOP_SOLDER_LAYER = Layer(7, "TopSolderLayer", "#800080", True, False, False)
        self.BOTTOM_SOLDER_LAYER = Layer(8, "BottomSolderLayer", "#AA00FF", True, False, False)
        self.RAT_LINES_LAYER = Layer(9, "Ratlines", "#6464FF", True, False, True)
        self.BOARD_OUTLINE_LAYER = BoardOutlineLayer(10, "BoardOutline", "#FF00FF", True, False, True)
        self.MULTI_LAYER_LAYER = Layer(11, "Multi-layer", "#C0C0C0", True, False, True)
        self.DOCUMENT_LAYER = Layer(12, "Document", "#FFFFFF", True, False, True)

        for inner_layer in range(1, copper_layers - 1):
            print("EXTRA LAYER")
            self.__setattr__(
                f"INNER_{inner_layer}_LAYER",
                InnerCopperLayer(
                    20 + inner_layer,
                    f"Inner{inner_layer}",
                    color="#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)]),
                    visible=True,
                    active=False,
                    config=True,
                ),
            )

        self.shapes = []
        for layer in self.layers:
            layer._pcb = self

    def add_hole(self, diameter: float, center: Point = Point(0, 0), locked: bool = False):
        locked = 1 if locked else 0
        diameter = diameter / 20.0
        id_ = f"gge{datetime.datetime.now().timestamp()}".replace(".", "")
        self.shapes.append(f"HOLE~{center.x / 10.0}~{center.y / 10.0 * -1}~{diameter}~{id_}~{locked}")

    def add_via(
            self, diameter: float, hole_diameter: float, center: Point = Point(0, 0), net: str = "",
            locked: bool = False
    ):
        locked = 1 if locked else 0
        id = f"gge{datetime.datetime.now().timestamp()}".replace(".", "")
        self.shapes.append(
            f"VIA~{center.x / 10.0}~{center.y / 10.0 * -1}~{diameter / 10.0}~{net}~{hole_diameter / 20}~{id}~{locked}"
        )

    @property
    def layers(self):
        out = []
        for attr_name, attr in self.__dict__.items():
            if "_LAYER" in attr_name:
                out.append(attr)
        return out

    def __repr__(self):
        source = {
            "head": f"{self.document_type}~{self.version}",
            "canvas": self.canvas,
            "shape": self.shapes,
            "layers": self.layers,
        }
        return json.dumps(source, default=lambda o: o.render(), indent=2)
