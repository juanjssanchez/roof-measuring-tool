import tkinter as tk
from tkinter import filedialog, simpledialog
from model import MeasurementMode
from collections import Counter

class MeasurementView:
    def __init__(self, root, model):
        self.root = root
        self.root.title("Measurement Tool")
        self.model = model

        # Create and configure canvas
        self.canvas = tk.Canvas(root)
        self.canvas.grid(row=0, column=0, columnspan=4, rowspan=4, sticky=tk.NSEW)
        self.canvas.config(width=900, height=600) # Initial canvas size

        # Set up resizing weights for rows and columns
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

        # Menu
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Create Shape Mode", command=self.set_create_shape_mode)
        file_menu.add_command(label="Edit Line Mode", command=self.set_edit_line_mode)
        file_menu.add_command(label="Generate Final Report", command=self.draw_report)

        model.selected_label = tk.StringVar()
        
        # Create a label selection frame
        self.label_frame = tk.Frame(self.root)
        self.label_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W)

        # Create label buttons
        self.label_buttons = []
        for i, label in enumerate(model.labels):
            label_button = tk.Radiobutton(
                self.label_frame,
                text=label,
                variable=model.selected_label,
                value=label,
            )
            self.label_buttons.append(label_button)
            label_button.grid(row=0, column=i, padx=5)
            label_button.configure(state="disabled")  # Initially disable the buttons

        # Set an initial value for the selected label
        model.selected_label.set(model.labels[0])


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
        self.model.mode = mode

        if mode == MeasurementMode.EDIT_LINE:
            for label_button in self.label_buttons:
                label_button.configure(state="normal")  # Enable buttons in edit mode
        else:
            for label_button in self.label_buttons:
                label_button.configure(state="disabled")  # Disable buttons in other modes

    def set_canvas(self, canvas):
        self.canvas = canvas
    
    def scale_prompt(self):
        return simpledialog.askfloat("Set Scale", "Enter the length of the reference line (in real-world units):")

    def draw_point(self, x, y, point_size, fill_color="red"):
        self.canvas.create_oval(x - point_size, y - point_size, x + point_size, y + point_size, fill=fill_color)

    def draw_line_segment(self, start, end, color="blue"):

        if self.model.mode == MeasurementMode.EDIT_LINE:
            if (start, end) in [(line.start, line.end) for line in self.model.lines]:
                # Check if the line's endpoints are in the list of lines
                line = [line for line in self.model.lines if (start, end) == (line.start, line.end)][0]
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
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=self.model.lineWidth)

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
        strLength = strLength * 3 # Sizes border based on text length
        text_bbox = (x - strLength, y - 10, x + strLength, y + 10)

        # Create a background rectangle
        self.canvas.create_rectangle(text_bbox, fill="white")
        # Create the text on top of the rectangle
        self.canvas.create_text(x, y, text=text, fill=fill)

    def fill_shape(self, shape, alpha=0.5):

        self.canvas.create_polygon(shape.vertices, fill="white", outline="", stipple='gray12', width=2)

    def draw_report(self):

        distanceList, distanceTotal, labelList, areaList, areaTotal, string_counts = self.model.generate_report()

        # Create a new window to display the report
        report_window = tk.Toplevel()
        report_window.title("Final Report")

        # Create a text widget
        report_text = tk.Text(report_window, wrap="word", height=20, width=60)
        report_text.grid(row=0, column=0, padx=10, pady=10)

        # Insert the content into the widget
        report_text.insert(tk.END, "List of distances: " + distanceList + "\n")
        report_text.insert(tk.END, "Total Distance: " + str(round(distanceTotal, 2)) + "\n\n")
        report_text.insert(tk.END, "List of areas: " + areaList + "\n")
        report_text.insert(tk.END, "Total Area: " + str(round(areaTotal, 2)) + "\n\n")
        report_text.insert(tk.END, "Counts:\n")
        for string, count in string_counts.items():
            report_text.insert(tk.END, f"{string}: {count}\n")

        # Make the text widget read-only
        report_text.configure(state=tk.DISABLED)