from model import MeasurementMode
from model import LineSegment
from model import Shape

class MeasurementController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.canvas.bind("<Button-1>", self.on_click)  # Bind the canvas click event
        self.view.canvas.bind("<Button-3>", self.on_right_click) # Right click to select lines

        # Bind the pitch listbox click events
        self.view.pitch_list.listbox.bind("<Button-1>", self.on_pitch_list_click)

    def on_click(self, event):
        # CREATING LINES/SHAPES MODE
        if self.model.mode == MeasurementMode.CREATE_SHAPE:
            x, y = event.x, event.y

            # Check for a preexisting vertex
            for shape in self.model.shapes:
                for vertex in shape.vertices:
                    if self.is_close_to_point((x,y), vertex):
                        (x,y) = vertex  # Set existing vertex as the current vertex
            # Check if current point is close to the first point (completing the shape)(this is messy)
            if self.model.points and self.is_close_to_point((x,y), self.model.points[0]):
                (x, y) = self.model.points[0]

            self.model.points.append((x, y))
            self.view.draw_point(x, y, self.model.pointSize)

            # Draw line
            if len(self.model.points) > 1:            
                current_line = self.model.points[-2], self.model.points[-1]

                # Check if line segment exists
                for line in self.model.lines:
                    if (line.start, line.end) == current_line or (line.end, line.start) == current_line:
                        break
                else:
                    self.model.lines.append(LineSegment(*current_line)) # Store line if it doesnt exist already
                    self.view.draw_line_segment(current_line[0], current_line[1])

                # Set the scale for first line
                if len(self.model.points) == 2 and self.model.scale == None:
                    reference_length= self.view.scale_prompt()
                    self.model.set_scale(self.model.lines[-1], reference_length)

            # Calculate distance between points
            if len(self.model.points) >= 2 and self.model.scale:
                self.model.lines[-1].distance = LineSegment.calculate_distance(self.model.lines[-1], self.model.scale)
                self.view.draw_line_measurement(self.model.lines[-1])

            # Check if shape should be closed
            if len(self.model.points) >= 3 and self.is_close_to_point(self.model.points[0], self.model.points[-1]):
                self.model.shapes.append(Shape(self.model.points[:]))  # Store the shape
                self.model.points = []  # Reset points for the next shape
                self.model.shapes[-1].area = Shape.area_including_pitch(self.model.shapes[-1], self.model.scale)
                self.view.draw_area(self.model.shapes[-1], self.model.shapes[-1].area)
        
        # EDIT LINE MODE
        elif self.model.mode == MeasurementMode.EDIT_LINE:
            # Check if the click selects a line
            for line in self.model.lines:
                if self.is_point_on_line(event.x, event.y, line):
                    
                    if self.model.selected_line:
                        self.view.draw_line_segment(self.model.selected_line.start, self.model.selected_line.end)
                    # Highlight the selected line
                    self.model.selected_line = line
                    self.view.draw_line_segment(line.start, line.end)
                    # Set the label of the selected line to the chosen label
                    self.model.selected_line.label = self.model.selected_label.get()
                    break
            else:
                # Clear the selection and return color
                if self.model.selected_line:
                    self.view.draw_line_segment(
                        self.model.selected_line.start, self.model.selected_line.end
                    )
                self.model.selected_line = None

    def is_close_to_point(self, point1, point2):
        # Check if the distance between two points is close enough to consider them the same point
        x1, y1 = point1
        x2, y2 = point2

        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5 < 5
    
    def is_point_on_line(self, x, y, line):
        # check if a point is near a line defined by its endpoints
        x1, y1 = line.start
        x2, y2 = line.end
        distance = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance < 5  # Tolerance
    
    def is_point_in_shape(self, x, y, shape):
        # Check if a point is inside a given shape using the Ray Casting algorithm
        num_vertices = len(shape.vertices)

        intersect_count = 0
        for i in range(num_vertices):
            x1, y1 = shape.vertices[i]
            x2, y2 = shape.vertices[(i + 1) % num_vertices]  # Wrap around for the last edge

            # Check if the point is above, below, or on the edge
            if (y1 <= y < y2) or (y2 <= y < y1):
                # Check if the ray crosses the edge
                if x1 + (y - y1) / (y2 - y1) * (x2 - x1) < x:
                    intersect_count += 1

        # If the number of intersections is odd, the point is inside the polygon
        return intersect_count % 2 == 1


    def on_pitch_list_click(self, event):
        index = self.view.pitch_list.listbox.nearest(event.y)
        pitch = self.view.pitch_list.update_selected_pitch(index)
        print(pitch)


    def on_right_click(self, event):
        x, y = event.x, event.y

        # Check if clicked on shape
        for shape in self.model.shapes:
            if self.is_point_in_shape(x, y, shape):
                print(shape.pitch)
                return
