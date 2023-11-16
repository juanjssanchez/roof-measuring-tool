from collections import Counter
from LineSegment import LineSegment
from MeasurementMode import MeasurementMode
from Shape import Shape

class MeasurementModel:
    def __init__(self):
        self.image = None
        self.scale = None
        self.mode = MeasurementMode.CREATE_SHAPE # Current mode

        self.points = []    # Stores vertices of the current shape
        self.shapes = []    # Stores multiple shapes as a list of lists
        self.lines = []     # Stores LineSegment instances

        self.selected_line = None   # Store the currently selected line
        self.selected_label = ""    # Store the selected label

        self.pointSize = 3  # Default
        self.lineWidth = 3  # Default
        self.labels = ["Ridge", "Valley", "Rake", "Eave"]

    
    def set_scale(self, reference_line, reference_length):
        reference_line = reference_line if self.lines else None

        if reference_length:
            x1, y1 = reference_line.start
            x2, y2 = reference_line.end
            distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            self.scale = distance_pixels / reference_length

    def generate_report(self):
        distanceList = ""
        distanceTotal = 0
        labelList = []
        for line in self.lines:
            distanceList += f"{round(line.distance, 2)}, "
            labelList.append(line.label)
            distanceTotal += line.distance
        print("List of distances: " + distanceList)
        print("Total Distance: ", round(distanceTotal, 2))

        areaList = ""
        areaTotal = 0
        for shape in self.shapes:
            areaList += f"{round(shape.area, 2)}, "
            areaTotal += shape.area
        print("List of areas: " + areaList)
        print("Total Area: ", round(areaTotal, 2))

        # Count how many ridges, valleys, etc
        string_counts = {}
        string_counts = Counter(labelList)
        for string, count in string_counts.items():
            print(f"{string}: {count}")
