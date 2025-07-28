from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
from shapely.geometry import Polygon

class Category(Enum):
    DOOR = auto()
    WINDOW = auto()
    STAIRS = auto()
    WALL = auto()
    OVEN = auto()
    CHAIR = auto()
    TABLE = auto()
    BED = auto()
    SINK = auto()
    SOFA = auto()
    TUB = auto()
    COLUMN = auto()
    RAILING = auto()


@dataclass
class Point:
    x: float
    y: float

@dataclass
class Edge:
    a: Point
    b: Point


@dataclass
class BBox:
    a: Point  
    b: Point  
    c: Point  
    d: Point

    def as_list(self) -> list[Point]:
        return [self.a, self.b, self.c, self.d]
    
# Represents a floor plan symbol such as a window, door, etc. 
@dataclass(frozen=True)
class Symbol:
    category: Category
    bbox: BBox


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
    def from_junctions(cls, json_data):
        polygon = Polygon([(x, y) for x, y in json_data["room"]])
        return cls(polygon)

    @property
    def edges(self) -> list[Edge]:
        coords = list(self.polygon.exterior.coords[:-1])  # Remove duplicate last point
        edges = []
        
        for i in range(len(coords)):
            current = Point(coords[i][0], coords[i][1])
            next_point = Point(coords[(i + 1) % len(coords)][0], coords[(i + 1) % len(coords)][1])
            edges.append(Edge(current, next_point))
        return edges

    def __str__(self):
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
    
