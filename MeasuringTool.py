import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

class MeasurementMode:
    CREATE_SHAPE = "Create Shape"
    EDIT_LINE = "Edit Line"

class LineSegment:
    def __init__(self, start, end, color="blue"):
        self.start = start
        self.end = end
        self.color = color
        self.distance = None
        self.label = None

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
        self.canvas.config(width=900, height=600) #initial canvas size
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click to select lines
        
        self.image = None
        self.scale = None
        
        self.mode = MeasurementMode.CREATE_SHAPE # current mode
        
        self.points = []  # Stores vertices of the current shape
        self.shapes = []  # Stores multiple shapes as a list of lists
        self.lines = []   # Stores LineSegment instances

        self.reference_line = None

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
        self.reference_line = self.lines[-1] if self.lines else None

        reference_length = simpledialog.askfloat("Set Scale", "Enter the length of the reference line (in real-world units):")
        if reference_length:
            x1, y1 = self.reference_line.start
            x2, y2 = self.reference_line.end
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
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")

            # Draw line
            if len(self.points) > 1:            
                current_line = self.points[-2], self.points[-1]

                # Check if line segment exists
                for line in self.lines:
                    if (line.start, line.end) == current_line or (line.end, line.start) == current_line:
                        break
                else:
                    self.lines.append(LineSegment(*current_line)) # Store line if it doesnt exist already
                    self.draw_line_segment(current_line[0], current_line[1], color="blue")

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
                        self.draw_line_segment(self.selected_line.start, self.selected_line.end, color="blue")
                    # Highlight the selected line
                    self.selected_line = line
                    self.draw_line_segment(line.start, line.end, color="red")
                    # Set the label of the selected line to the chosen label
                    self.selected_line.label = self.selected_label.get()
                    break
            else:
                # Clear the selection and return color
                if self.selected_line:
                    self.draw_line_segment(
                        self.selected_line.start, self.selected_line.end, color="blue"
                    )
                self.selected_line = None


    def is_close_to_point(self, point1, point2):
        # Check if the distance between two points is close enough to consider them the same point
        x1, y1 = point1
        x2, y2 = point2

        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5 < 5
    
    def draw_line_segment(self, start, end, color="blue"):
        x1, y1 = start
        x2, y2 = end
        self.canvas.create_line(x1, y1, x2, y2, fill=color)

    def draw_line_measurement(self, line, color="green"):
        x1, y1 = line.start
        x2, y2 = line.end

        scale_label_x = (x1 + x2) / 2
        scale_label_y = (y1 + y2) / 2
        self.canvas.create_text(scale_label_x, scale_label_y, text=f"{line.distance:.2f} units", fill=color)

    def draw_area(self, shape, area,  alpha=0.5):
        # Calculate the center of the shape
        x_coords, y_coords = zip(*shape.vertices)
        center_x = sum(x_coords) / len(shape.vertices)
        center_y = sum(y_coords) / len(shape.vertices)

        # Display the area measurement at the center and fill
        self.fill_shape(shape)
        self.canvas.create_text(center_x, center_y, text=f"{area:.2f} sq. units", fill="black")

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

            
    def is_point_on_line(self, x, y, line):
        # check if a point (x, y) is near a line defined by its endpoints
        x1, y1 = line.start
        x2, y2 = line.end
        distance = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance < 5  # Tolerance
    
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
        lineList = ""
        distanceTotal = 0
        for line in self.lines:
            lineList += f"{round(line.distance, 2)}, "

            distanceTotal += line.distance
        print("list of distances: " + lineList)
        print("Total Distance: ", round(distanceTotal, 2))

        areaList = ""
        areaTotal = 0
        for shape in self.shapes:
            areaList += f"{round(shape.area, 2)}, "
            areaTotal += shape.area
        print("list of areas: " + areaList)
        print("Total Area: ", round(areaTotal, 2))

if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementApp(root)
    root.mainloop()
