import tkinter as tk
from model import MeasurementModel
from view import MeasurementView
from controller import MeasurementController

if __name__ == "__main__":
    root = tk.Tk()
    model = MeasurementModel()
    view = MeasurementView(root, model)
    controller = MeasurementController(model, view)
    root.mainloop()
