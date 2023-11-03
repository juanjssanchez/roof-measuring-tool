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
        self.points = []
        self.reference_line = None
        self.scale = None

        self.prevPoint = None
        self.currPoint = -1

        # Create a menu
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Set Scale", command=self.set_scale)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.image = tk.PhotoImage(file=file_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)


    def set_scale(self):
        if self.reference_line is None:
            tk.messagebox.showwarning("Warning", "Please create a reference line first.")
            return

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

        self.currPoint += 1
        self.prevPoint = self.currPoint - 1
        
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")
        
        if len(self.points) == 2 and self.reference_line is None:
            self.reference_line = self.points
            self.canvas.create_line(self.reference_line, fill="green")
        elif len(self.points) >= 2 and self.scale:
            distance = self.calculate_distance(self.points[self.prevPoint], self.points[self.currPoint])
            print(f"Distance: {distance} units")
    
    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        # Calculate the distance in pixels
        distance_pixels = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        # Calculate the distance in scaled units
        distance_units = distance_pixels / self.scale
        return distance_units


if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementApp(root)
    root.mainloop()
