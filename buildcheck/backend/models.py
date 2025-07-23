class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Edge:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
    def __str__(self):
        return f"Edge(start=({self.start.x}, {self.start.y}), end=({self.end.x}, {self.end.y}))"

class Symbol:
    def __init__(self, category: str, bbox: list[float, float, float, float]):
        self.category = category  # e.g., 'door', 'window'
        self.bbox = bbox          # (x_min, y_min, x_max, y_max)
    def __str__(self):
        return f"Symbol(category={self.category}, bbox={self.bbox})"

class Dimension:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    def __str__(self):
        return f"Dimension(width={self.width}, height={self.height})"

class Room:
    def __init__(
        self,
        corners: list[Point],  # 4 points
        symbols: list[Symbol] = [],
        label: list[str] = [],
        dimension: list[Dimension] = []
    ):
        self.corners = corners
        self.symbols = symbols
        self.label = label
        self.dimension = dimension
    
    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["room"])

    @property
    def edges(self) -> list[Edge]:
        # Returns the 4 edges of the room
        return [Edge(self.corners[i], self.corners[(i+1)%4]) for i in range(4)]
    def __str__(self):
        return f"Room(corners={self.corners}, symbols={self.symbols}, label={self.label}, dimension={self.dimension})"

class Layout:
    def __init__(
        self,
        rooms: list[Room] = [],
        metadata: list[dict] = []
    ):
        self.rooms = rooms
        self.metadata = metadata or {}

    def add_room(self, room: Room):
        self.rooms.append(room)
    
# Testing the classes
# room_data = {"room": [(10, 20), (30, 20), (30, 40), (10, 40)]}
# room = Room.from_json(room_data)
# room.label = "Living Room"
# room.dimensions = (20, 20)
# room.symbols.append(Symbol("door", (12, 22, 4, 1)))

# print(room)

# layout = Layout()
# layout.add_room(room)
