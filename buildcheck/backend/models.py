class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Edge:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

class Symbol:
    def __init__(self, category: str, bbox: Tuple[float, float, float, float]):
        self.category = category  # e.g., 'door', 'window'
        self.bbox = bbox          # (x_min, y_min, x_max, y_max)

class Dimension:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

class Room:
    def __init__(
        self,
        corners: List[Point],  # 4 points
        symbols: Optional[List[Symbol]] = None,
        label: Optional[str] = None,
        dimension: Optional[Dimension] = None
    ):
        self.corners = corners
        self.symbols = symbols or []
        self.label = label
        self.dimension = dimension

    @property
    def edges(self) -> List[Edge]:
        # Returns the 4 edges of the room
        return [Edge(self.corners[i], self.corners[(i+1)%4]) for i in range(4)]

class Layout:
    def __init__(
        self,
        rooms: List[Room],
        metadata: Optional[dict] = None
    ):
        self.rooms = rooms
        self.metadata = metadata or {}