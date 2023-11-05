import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Tool")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.image = None
        self.scale = None
        self.points = []  # Stores vertices of the current shape
        self.shapes = []  # Stores multiple shapes as a list of lists

        self.reference_line = None

        # Create a menu
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Set Scale", command=self.set_scale)
        file_menu.add_command(label="Calculate Area", command=self.calculate_area)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.image = tk.PhotoImage(file=file_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def set_scale(self):
        self.reference_line = self.points
        reference_length = simpledialog.askfloat("Set Scale", "Enter the length of the reference line (in real-world units):")
        if reference_length:

            x1, y1 = self.reference_line[0]
            x2, y2 = self.reference_line[1]
            distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            self.scale = distance_pixels / reference_length

            scale_label_x = (self.reference_line[0][0] + self.reference_line[1][0]) / 2
            scale_label_y = (self.reference_line[0][1] + self.reference_line[1][1]) / 2
            self.canvas.create_text(scale_label_x, scale_label_y, text=f"Scale: {reference_length:.2f} units", fill="green")
            print(f"Scale set to {reference_length} units")

    def on_click(self, event):

        x, y = event.x, event.y
        self.points.append((x, y))

        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")

        # draw line
        if len(self.points) > 1:
            self.canvas.create_line(self.points[-2], self.points[-1], fill="blue")
            # set the scale for first line
            if len(self.points) == 2 and self.scale == None:
                self.set_scale()

        # calculate distance between points
        if len(self.points) >= 2 and self.scale:
            distance = self.calculate_distance(self.points[-2], self.points[-1])
            print(f"Distance: {distance} units")

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
    
    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        # Calculate the distance in pixels
        distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        # Calculate the distance in scaled units
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
