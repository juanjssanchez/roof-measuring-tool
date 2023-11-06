import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

class LineSegment:
    def __init__(self, start, end, color="blue"):
        self.start = start
        self.end = end
        self.color = color
        self.distance = None

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Tool")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click to select lines
        
        self.image = None
        self.scale = None
        
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
        file_menu.add_command(label="Set Scale", command=self.set_scale)
        file_menu.add_command(label="Calculate Area", command=self.calculate_area)
        
        # Store the currently selected line
        self.selected_line = None

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.image = tk.PhotoImage(file=file_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def set_scale(self):
        self.reference_line = self.lines[-1] if self.lines else None

        reference_length = simpledialog.askfloat("Set Scale", "Enter the length of the reference line (in real-world units):")
        if reference_length:
            x1, y1 = self.reference_line.start
            x2, y2 = self.reference_line.end
            distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            self.scale = distance_pixels / reference_length

    def on_click(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")

        # draw line
        if len(self.points) > 1:            
            line = self.points[-2], self.points[-1]
            self.lines.append(LineSegment(*line))
            self.draw_line_segment(line[0], line[1], color="blue")
            
            # set the scale for first line
            if len(self.points) == 2 and self.scale == None:
                self.set_scale()

        # calculate distance between points
        if len(self.points) >= 2 and self.scale:
            self.lines[-1].distance = self.calculate_distance(self.lines[-1])
            self.draw_line_measurement(self.lines[-1])
            print(f"Distance: {self.lines[-1].distance} units")

        # check if shape should be closed
        if len(self.points) >= 3 and self.is_close_to_first_point(self.points[0], self.points[-1]):
            self.shapes.append(self.points[:])  # Store the shape
            self.points = []  # Reset points for the next shape
            # AREA NEEDS FIXING
            self.calculate_area()


    def is_close_to_first_point(self, point1, point2):
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

    def on_right_click(self, event):
        x, y = event.x, event.y
        # Check if the click selects a line
        for line in self.lines:
            if self.is_point_on_line(x, y, line):
                # Highlight the selected line
                self.selected_line = line
                print(self.selected_line.distance)
                self.draw_line_segment(line.start, line.end, color="red")
                break
        else:
            # If the click did not select a line, clear the selection
            self.selected_line = None

    def is_point_on_line(self, x, y, line):
        # Check if a point (x, y) is near a line defined by its endpoints
        x1, y1 = line.start
        x2, y2 = line.end
        distance = abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance < 5  # Tolerance
    
    def calculate_distance(self, line):
        (x1, y1), (x2, y2) = line.start, line.end
        distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        distance_units = distance_pixels / self.scale
        return distance_units

    def calculate_area(self):
        for shape in self.shapes:
            area = self.calculate_polygon_area(shape)
            print(f"Area of shape: {area} square units")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementApp(root)
    root.mainloop()
