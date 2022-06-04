# Fractals
A project for CSE163, where we compare methods for computing the power of a fractal, and utilize these methods to analyze the world around us.

## Getting Started
Install all of the dependencies for this project with

```
pip3 install -r requirements.txt
```

`geopandas` is also a required but I could not find an easy way to install it on windows. If you are on mac or linux you should be able to install this using
```
pip3 install geopandas
```
however, on a windows machine, `roughness.py` will not compile without `geopandas` I would recomend using a virutal enviroment on edstem, or VirutalBox

## Compiling the Data
some of the data is already included, such as `state_borders`, and `basic_shapes`. These where accuried and drawn by hand, so we dont include a module to compile these. However the majority of the data is scraped in real-time

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
To analyze images with Machine Learning, run
```
python3 ml.py
```

## Border Analysis
To analyze the borders of US State geospatial data
```
python3 roughness.py
```

## Testing
In order to test all of the modules in this repo run
```
python3 tests.py
```
this will error out if there is unexpected behavior in any function