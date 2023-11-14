import math


class Shape:
    def __init__(self, vertices):
        self.vertices = vertices
        self.area = None
        self.pitch = (6, 12)  # Default pitch (6/12)

    def area_including_pitch(self, scale):
        rise, run = self.pitch
        multiplier = math.sqrt( ((rise/run) * (rise/run)) + 1 )   # Roof Pitch Multiplier Formula 

        area = self.calculate_flat_area(scale)

        return area * multiplier

    def calculate_flat_area(self, scale):
        area = self.calculate_polygon_area(self.vertices)
        area_units = area / (scale ** 2)  # convert pixels to units
        return area_units

    def calculate_polygon_area(self,vertices):
        # Calculate the area of a polygon using the shoelace formula
        n = len(vertices)
        if n < 3:
            return 0

        area = 0
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            area += (x1 * y2 - x2 * y1)

        return abs(area) / 2