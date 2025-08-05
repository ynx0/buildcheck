from dataclasses import dataclass
from enum import Enum
from typing import Union
from shapely.geometry import Polygon



def is_4_point_polygon(polygon: Polygon) -> bool:
    coords = list(polygon.exterior.coords)
    return len(coords) == 5 and len(set(coords[:-1])) == 4  # 4 unique + 1 closing point



# must match from the model, i.e. YOLO(...).names
class Category(Enum):
    COLUMN = 0
    CURTAIN_WALL = 1
    DIMENSION = 2
    DOOR = 3
    RAILING = 4
    SLIDING_DOOR = 5
    STAIR_CASE = 6
    WALL = 7
    WINDOW = 8



# Represents a floor plan symbol such as a window, door, etc. 
@dataclass(frozen=True)
class Symbol:
    category: Category
    bbox: Polygon

    def __post_init__(self):
        if not is_4_point_polygon(self.bbox):
            raise ValueError(f"bbox failed 4pt test {self.bbox=}")


# Metadata Definitions
@dataclass
class Label:
    text: str
#A class that represents the width and height of a room recovered from the OCR process
@dataclass
class Dimension:
    width: float
    height: float

Metadata = Union[Label, Dimension]

class Room:
    def __init__(
        self,
        polygon: Polygon,  
        symbols: list[Symbol] = None,
        metadata: list[Metadata] = None,
    ):
        self.polygon = polygon
        self.symbols = symbols if symbols is not None else []  # NEW LIST!
        self.metadata = metadata if metadata is not None else []

    @classmethod
    def from_junctions(cls, junctions):
        """
        junctions: cw/ccw ordered points that make up a polygon
        """
        polygon = Polygon([(x, y) for x, y in junctions])
        return cls(polygon)

    @property
    def name(self) -> str:
        name = ""
        for data in self.metadata:
            if isinstance(data, Label):
                name += " " + data.text
        return name

    @property
    def dims(self) -> list[Dimension]:
        return list(filter(lambda m: isinstance(m, Dimension), self.metadata))


    def __repr__(self):
        return (
            f"Room(polygon={self.polygon}, "
            f"symbols={self.symbols}, metadata=({self.metadata})"
        )

class Layout:
    def __init__(self, rooms: list[Room] = None, metadata: list[Metadata] = None, file_name: str = None):
        self.rooms = rooms if rooms is not None else []
        self.metadata = metadata if metadata is not None else []
        self.file_name = file_name

    def add_room(self, room: Room):
        self.rooms.append(room)
    
