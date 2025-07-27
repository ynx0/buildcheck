from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

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

    def __str__(self):
        return f"Edge(a=({self.a.x}, {self.a.y}), b=({self.b.x}, {self.b.y}))"
    

@dataclass
class BBox:
    a: Point  
    b: Point  
    c: Point  
    d: Point  
    def as_list(self) -> list[Point]:
        return [self.a, self.b, self.c, self.d]
    
# Represents a floor plan symbol such as a window, door, etc. 
@dataclass
class Symbol:
    category: Category
    bbox: BBox

    def __str__(self):
        return f"Symbol(category={self.category}, bbox={self.bbox})"
    

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
        junctions: list[Point],  
        symbols: list[Symbol] = None,
        metadata: list[Metadata] = None,
        edges: list[Edge] = []
    ):
        self.junctions = junctions
        self.symbols = symbols if symbols is not None else []  # NEW LIST!
        self.metadata = metadata if metadata is not None else []
        self.edges = edges

    @classmethod
    def from_json(cls, json_data):
        points = [Point(x, y) for x, y in json_data["room"]]
        return cls(points)


    def __str__(self):
        return (
            f"Room(junctions={self.junctions}, "
            f"symbols={self.symbols}, metadata=({self.metadata})"
        )

class Layout:
    def __init__(
        self,
        rooms: list[Room] = [],
        metadata: list[Metadata] = [],
        file_name: str = None,
    ):
        self.rooms = rooms
        self.metadata = metadata
        self.file_name = file_name

    def add_room(self, room: Room):
        self.rooms.append(room)
    
