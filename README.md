# Roof Measuring Tool - a simple roofing estimator

This measuring tool can be used to outline a roof and generate a rough estimate of square footage, materials needed, etc. You can import a photo of any roof and start outlining as long as you know the measurement of at least 1 edge of the roof. You can also edit the edges in order to specify what type of edge it is (ridge, valley, etc). 

<img src="https://github.com/juanjssanchez/measuringtool/assets/47364524/8bb774b1-b27b-4028-8ef5-3dac9669ca2d" width="650">

## Why?
Normally you would have to be on site to take the measurements of a roof then make your estimate afterwards. Sometimes you just want to make a quick estimate without needing to pull out the ladder so I made this program which will help you get real world measurements of any roof without ever stepping outside.

## Quick Start
Simply download the project and run main.py.

```
python main.py
```

Once the Tkinter window appears, click the File drop down menu and open an image of the roof you want to measure.

### Setting the scale
<img src="https://github.com/juanjssanchez/measuringtool/assets/47364524/8fd2418e-39be-44ac-8183-4b695e2fb9c1" width="500">

The first line you create will prompt you to enter the real world measurement (ft) for that line. You can use the google maps distance tool to get this number if you don't already have a real world measurement. This reference line must be relatively accurate in order for the rest of the measurements to be properly scaled.


## Usage

### Outlining

Click a corner of a roof face to begin outlining. Click the remaining corners of the roof face until you "close" the shape by reaching the first dot again. Closing a shape will automatically shade it in and give the estimated surface area for that specific section. Repeat this for every slope. 

Make sure to click the existing points if you are outlining a slope that shares an edge with a shape you have already created.

### Labeling edges
<img src="https://github.com/juanjssanchez/measuringtool/assets/47364524/ca385c34-d67d-4300-bed9-24080a706ca9" width="500">

In the drop down menu, click Edit Line Mode to start labeling the edges. At the bottom of the screen you can choose a label type (such as Ridge or Valley) and simply click on a line to label it. This will allow you to specify what kind of edge it is in order to help you with your materials.

### Generate Final Report

When you are done outlining and labeling you can click the drop down menu to generate a final report. The report will list out all the values and details of the roof, such as total surface area or number of valley edges.
