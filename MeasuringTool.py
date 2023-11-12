import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from collections import Counter

class MeasurementMode:
    CREATE_SHAPE = "Create Shape"
    EDIT_LINE = "Edit Line"

class LineSegment:
    def __init__(self, start, end, color="blue"):
        self.start = start
        self.end = end
        self.distance = None
        self.label = "Eave"

class Shape:
    def __init__(self, vertices):
        self.vertices = vertices
        self.area = None

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Tool")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.config(width=900, height=600) # Initial canvas size
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click to select lines
        
        self.image = None
        self.scale = None
        
        self.mode = MeasurementMode.CREATE_SHAPE # Current mode
        
        self.points = []  # Stores vertices of the current shape
        self.shapes = []  # Stores multiple shapes as a list of lists
        self.lines = []   # Stores LineSegment instances

        self.pointSize = 3 # default
        self.lineWidth = 3 # default

        # Menu
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Create Shape Mode", command=self.set_create_shape_mode)
        file_menu.add_command(label="Edit Line Mode", command=self.set_edit_line_mode)
        file_menu.add_command(label="Generate Final Report", command=self.generate_report)
        
        # Store the currently selected line
        self.selected_line = None

        # Store the selected label
        self.selected_label = tk.StringVar()

        # Create a label selection frame
        self.label_frame = tk.Frame(self.root)
        self.label_frame.pack()

        # Create label buttons
        labels = ["Ridge", "Valley", "Rake", "Eave"]
        self.label_buttons = []
        for label in labels:
            label_button = tk.Radiobutton(
                self.label_frame,
                text=label,
                variable=self.selected_label,
                value=label,
            )
            self.label_buttons.append(label_button)
            label_button.pack(side=tk.LEFT)
            label_button.configure(state="disabled")  # Initially disable the buttons

        # Set an initial value for the selected label
        self.selected_label.set(labels[0])

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.image = tk.PhotoImage(file=file_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
    
    # Mode switching
    def set_create_shape_mode(self):
        self.set_mode(MeasurementMode.CREATE_SHAPE)

    def set_edit_line_mode(self):
        self.set_mode(MeasurementMode.EDIT_LINE)

    def set_mode(self, mode):
        self.mode = mode

        if mode == MeasurementMode.EDIT_LINE:
            for label_button in self.label_buttons:
                label_button.configure(state="normal")  # Enable buttons in edit mode
        else:
            for label_button in self.label_buttons:
                label_button.configure(state="disabled")  # Disable buttons in other modes

    def set_scale(self):
        reference_line = self.lines[-1] if self.lines else None

        reference_length = simpledialog.askfloat("Set Scale", "Enter the length of the reference line (in real-world units):")
        if reference_length:
            x1, y1 = reference_line.start
            x2, y2 = reference_line.end
            distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            self.scale = distance_pixels / reference_length


    def on_click(self, event):
        # CREATING LINES/SHAPES MODE
        if self.mode == MeasurementMode.CREATE_SHAPE:
            x, y = event.x, event.y

            # Check for a preexisting vertex
            for shape in self.shapes:
                for vertex in shape.vertices:
                    if self.is_close_to_point((x,y), vertex):
                        (x,y) = vertex  # Set existing vertex as the current vertex
            # Check if current point is close to the first point (completing the shape)(this is messy)
            if self.points and self.is_close_to_point((x,y), self.points[0]):
                (x, y) = self.points[0]

            self.points.append((x, y))
            self.canvas.create_oval(x-self.pointSize, y-self.pointSize, x+self.pointSize, y+self.pointSize, fill="red")

            # Draw line
            if len(self.points) > 1:            
                current_line = self.points[-2], self.points[-1]

                # Check if line segment exists
                for line in self.lines:
                    if (line.start, line.end) == current_line or (line.end, line.start) == current_line:
                        break
                else:
                    self.lines.append(LineSegment(*current_line)) # Store line if it doesnt exist already
                    self.draw_line_segment(current_line[0], current_line[1])

                # Set the scale for first line
                if len(self.points) == 2 and self.scale == None:
                    self.set_scale()

            # Calculate distance between points
            if len(self.points) >= 2 and self.scale:
                self.lines[-1].distance = self.calculate_distance(self.lines[-1])
                self.draw_line_measurement(self.lines[-1])

            # Check if shape should be closed
            if len(self.points) >= 3 and self.is_close_to_point(self.points[0], self.points[-1]):
                self.shapes.append(Shape(self.points[:]))  # Store the shape
                self.points = []  # Reset points for the next shape
                self.shapes[-1].area = self.calculate_area(self.shapes[-1])
                self.draw_area(self.shapes[-1], self.shapes[-1].area)
        
        # EDIT LINE MODE
        elif self.mode == MeasurementMode.EDIT_LINE:
            # Check if the click selects a line
            for line in self.lines:
                if self.is_point_on_line(event.x, event.y, line):
                    
                    if self.selected_line:
                        self.draw_line_segment(self.selected_line.start, self.selected_line.end)
                    # Highlight the selected line
                    self.selected_line = line
                    self.draw_line_segment(line.start, line.end)
                    # Set the label of the selected line to the chosen label
                    self.selected_line.label = self.selected_label.get()
                    break
            else:
                # Clear the selection and return color
                if self.selected_line:
                    self.draw_line_segment(
                        self.selected_line.start, self.selected_line.end
                    )
                self.selected_line = None


    def is_close_to_point(self, point1, point2):
        # Check if the distance between two points is close enough to consider them the same point
        x1, y1 = point1
        x2, y2 = point2

        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5 < 5
    
    def is_point_on_line(self, x, y, line):
        # check if a point (x, y) is near a line defined by its endpoints
        x1, y1 = line.start
        x2, y2 = line.end
        distance = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance < 5  # Tolerance


    def draw_line_segment(self, start, end):
        color = "blue"  # Default to blue color

        if self.mode == MeasurementMode.EDIT_LINE:
            if (start, end) in [(line.start, line.end) for line in self.lines]:
                # Check if the line's endpoints are in the list of lines
                line = [line for line in self.lines if (start, end) == (line.start, line.end)][0]
                label = line.label

                if label == "Valley":
                    color = "purple"
                elif label == "Eave":
                    color = "dark blue"
                elif label == "Rake":
                    color = "orange"
                elif label == "Ridge":
                    color = "pink"

        x1, y1 = start
        x2, y2 = end
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.lineWidth)

    def draw_line_measurement(self, line, color="green"):
        x1, y1 = line.start
        x2, y2 = line.end

        scale_label_x = (x1 + x2) / 2
        scale_label_y = (y1 + y2) / 2
        self.draw_text(scale_label_x, scale_label_y, f"{line.distance:.2f} f", color)

    def draw_area(self, shape, area,  alpha=0.5):
        # Calculate the center of the shape
        x_coords, y_coords = zip(*shape.vertices)
        center_x = sum(x_coords) / len(shape.vertices)
        center_y = sum(y_coords) / len(shape.vertices)

        # Display the area measurement at the center and fill
        self.fill_shape(shape)
        self.draw_text(center_x, center_y, f"{area:.2f} sqft", "black")

    def draw_text(self, x, y, text, fill):
        # Define a bounding box around the text
        strLength = len(text)
        strLength = strLength * 3 # sizes border based on text length
        text_bbox = (x - strLength, y - 10, x + strLength, y + 10)

        # Create a background rectangle
        self.canvas.create_rectangle(text_bbox, fill="white")
        # Create the text on top of the rectangle
        self.canvas.create_text(x, y, text=text, fill=fill)

    def fill_shape(self, shape, alpha=0.5):
        x_coords, y_coords = zip(*shape.vertices)

        self.canvas.create_polygon(shape.vertices, fill="white", outline="", stipple='gray12', width=2)


    def on_right_click(self, event):
        # Print the selected line label
        for line in self.lines:
            if self.is_point_on_line(event.x, event.y, line):
                # Highlight the selected line
                self.selected_line = line
                print(self.selected_line.label)

    
    def calculate_distance(self, line):
        (x1, y1), (x2, y2) = line.start, line.end
        distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        distance_units = distance_pixels / self.scale
        return distance_units

    def calculate_area(self, shape):
        area = self.calculate_polygon_area(shape.vertices)
        area_units = area / (self.scale ** 2)  # convert pixels to units
        return area_units

    def calculate_polygon_area(self, vertices):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementApp(root)
    root.mainloop()
