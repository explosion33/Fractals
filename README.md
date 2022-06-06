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
All of the data is already included you need to extract each of the foleders composed in `images.rar` into the main directory, on windows that is usually done with [winrar](https://www.win-rar.com/start.html?&L=0) or [7zip](https://www.7-zip.org/download.html). Alternitavely the folders can be downloaded directly from our [github page](https://github.com/explosion33/Fractals)

the directory should look as follows
```
Fractals\
    images\
    imgs\
    plts\
    state_borders\
    test_imgs\
    compileImages.py
    Fractal.py
    gz_2010_us_040_00_5m.json
    ImageTools.py
    ml.py
    README.md
    requirements.txt
    roughness.py
    tests.py
```

Some data was compiled and included by hand, `images`, `state_borders`, `gz_2010_us_040_00_5m.json`, `test_imgs`. The rest of the data, found in the `imgs` folder is pre-downloaded, but can also be re-downloaded by running


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