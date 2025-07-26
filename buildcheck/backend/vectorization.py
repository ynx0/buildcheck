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
    # Extend as needed


@dataclass
class Point(frozen=True):
    x: float
    y: float


@dataclass
class Edge(frozen=True):
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
@dataclass
class Symbol(frozen=True):
    category: Category
    bbox: BBox


# Metadata Definitions
@dataclass
class Label:
    text: str


#A class that represents the width and height of a room recovered from the OCR process
@dataclass
class Dimension(frozen=True):
    width: float
    height: float

Metadata = Union[Label, Dimension]



class Room:
    def __init__(
        self,
        junctions: list[Point],  
        symbols: list[Symbol] = [],
        metadata: list[Metadata] = [],
        edges: list[Edge] = []
    ):
        self.junctions = junctions
        self.symbols = symbols
        self.metadata = metadata
        self.edges = edges

    @classmethod
    def from_json(cls, json_data):
        points = [Point(x, y) for x, y in json_data["room"]]
        return cls(points)






class Layout:
    def __init__(
        self,
        rooms: list[Room] = [],
        file_name: str = None,
    ):
        self.rooms = rooms
        self.metadata = metadata
        self.file_name = file_name

    def add_room(self, room: Room):
        self.rooms.append(room)



