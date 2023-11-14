class LineSegment:
    def __init__(self, start, end, color="blue"):
        self.start = start
        self.end = end
        self.distance = None
        self.label = "Eave" # Default

    def calculate_distance(self, scale):
        (x1, y1), (x2, y2) = self.start, self.end
        distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        distance_units = distance_pixels / scale
        return distance_units