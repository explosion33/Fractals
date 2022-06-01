# Fractals
A project for CSE163, where we compare methods for computing the power of a fractal, and utilize these methods to analyze the world around us.

## Getting Started
Install all of the dependencies for this project with

```
pip3 install -r requirements.txt
```


## Compiling the Data
some of the data is already included, such as `state_borders`, and `basic_shapes`. However the majority of the data is scraped in real-time

In order to download this data run

```
python3 compileImages.py
```

this will download images into the `imgs` folder

## Fractal Analysis
A fractal can be analyzed with the following code snippet
```
from Fractal import Fractal
f = Fractal("path/to/img.png")
f.calculate_power()
```
There are also the following methods
```
f.visualize_counting()
f.get_last_power_visualization()
f.set_sample_size()
```

To run the analysis for the Fractal algorithm on the compiled datasets run
```
python3 Fractal.py
```
This will output the images you can see in the report to the `plts` folder


## ML Analysis
TODO

## Border Analysis
TODO

## Testing
In order to test all of the modules in this repo run
```
python3 tests.py
```
this will error out if there is unexpected behavior in any function