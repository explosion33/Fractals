"""
Ethan Armstrong
Section AD

This module contains the Fractal class which implements our Image Processing
Algorithim for determining Fractal power

There are also a couple of functions and a main() method used for running
our various datasets through the Fractal Algorithim
"""

import io
import os
import math
from PIL import Image
from multiprocessing import Process, Array
from matplotlib import pyplot as plt
from ImageTools import scaleImage


class Fractal:
    """
    A class for determining the power of a Fractal, as well as
    visualizing the Hausdorff process
    """
    def __init__(self, path) -> None:
        """
        Fractal() | creates a new Fractal object
        path | (str) full path to image this object will represent
        """
        self._img = Image.open(path)
        self._sample_size = 2

        self._vis_img = None
        self._power_vis = None

        self._OVERLAY_COLOR = (255, 255, 0, 100)

    def _get_background_color(self, img):
        """
        _get_background_color() | gets the background color of an image
            using the assumption that the background color is the most
            occuring color
        return | pixel in the image format, either: int, (int,int,int),
            (int, int, int, int) from 0-255
        """
        data = list(img.getdata())
        pixels = {}

        for pixel in data:
            if pixel not in pixels:
                pixels[pixel] = 0
            pixels[pixel] += 1

        pixel_freq = None
        for pixel, count in pixels.items():
            if pixel_freq is None or count > pixels[pixel]:
                pixel_freq = pixel

        return pixel_freq

    def _get_square_indicies(self, img, x, y):
        """
        _get_square_indicies() | gets the indicies for a square in the
            current image 1D stream, given the top left 2D location
        x | (int) x position of top-left corner of search square
        y | (int) y position of top-left corner of search square
        returns | list( (int) ) positions in 1D matrix
        """
        w = img.width
        h = img.height

        indicies = []
        for suby in range(self._sample_size):
            for subx in range(self._sample_size):
                if x+subx < w and y+suby < h:
                    index = ((w)*(y+suby)) + (x+subx)
                    indicies.append(index)

        return indicies

    def _count_non_background_pixels(self, img, generate_image=False):
        """
        _count_non_background_pixels() | counts the number of regions that
            contain a non background pixel
        img            | (PIL.Image) Image to count pixels of
        generate_image | (bool) (default = False), whether or not to visualize
            the counting algorithim
        returns | (int) | saves visualzation in Fractal._vis_image
        """
        bckg = self._get_background_color(img)

        if generate_image:
            self._vis_img = img.copy().convert("RGBA")

        data = list(img.getdata())
        w = img.width
        h = img.height

        count = 0
        for y in range(0, h, self._sample_size):
            for x in range(0, w, self._sample_size):
                # get the indexes in the current search square
                indexes = self._get_square_indicies(img, x, y)

                # check if any pixel in the search square contains a
                # non-bckg pixel
                containsPixel = False
                for index in indexes:
                    pixel = data[index]
                    if pixel != bckg:
                        containsPixel = True

                if containsPixel:
                    count += 1

                    # if the generate iamge flag is passed, we go through each
                    # pixel in the search area and set it to red if its a
                    # background pixel
                    if generate_image:
                        for index in indexes:
                            py = index // w
                            px = index % w

                            # if data[w*(py) + (px)] == bckg:
                            pixel = self._vis_img.getpixel((px, py))
                            alpha = self._OVERLAY_COLOR[3]

                            # mix overlay color with image base color
                            R = int((pixel[0]*(255-alpha) +
                                    self._OVERLAY_COLOR[0]*alpha)/255)
                            G = int((pixel[1]*(255-alpha) +
                                    self._OVERLAY_COLOR[1]*alpha)/255)
                            B = int((pixel[2]*(255-alpha) +
                                    self._OVERLAY_COLOR[2]*alpha)/255)

                            mixed = (R, G, B, 255)
                            self._vis_img.putpixel((px, py), mixed)
        return count

    def _get_num_places(self, x):
        """
        getNumPlaces() | gets the number of decimal places in a float/integer
        x | (float) (int)
        returns (int)
        """
        if int(x) == x:
            return 0
        return len(str(x)) - len(str(int(x))) - 1

    def _range_float(self, start, stop, step):
        """
        rangeF() | creates a list of numbers from start to stop by step
        start | (float) inclusive
        stop  | (float) exclusive
        step  | (float)
        returns (list( (float) ))
        """
        numplaces = self._get_num_places(step)
        out = []
        while True:
            out.append(start)
            start += step
            start = round(start, numplaces)
            if start >= stop:
                return out

    def _scale_count_process(self, factor, array):
        """
        _scale_count_process() | performs one step in the Hausdorff algorithm
            by scaling an image by a factor then counting the number of pixels
            modified to work in a Process object
        factor  | (float) factor to scale by
        array   | (multiprocessing.Array) shared memory to act as output
        returns | None | adds data to array [(float) factor, (float), count]
        """
        w, h = self._img.size
        scaledImg = scaleImage(self._img, (w*factor, h*factor))
        count = self._count_non_background_pixels(scaledImg)

        array[0] = factor
        array[1] = count
        return None

    def _get_scaling_data_process(self, start, stop, inc, verbose=False):
        """
        _get_scaling_data_process() | gets the scaling data for the fractal
            in a bunch of background processes. Scaling from start to stop,
            with an increment of inc
        start | (float) starting scale (inclusive)
        stop  | (float) ending scale   (exclusive)
        inc   | (float) amount to increment by
        """
        factors = self._range_float(start, stop, inc)
        procs = []
        for factor in factors:
            arr = Array('d', range(2))
            p = Process(target=self._scale_count_process, args=(factor, arr))
            p.start()

            procs.append((p, arr))

        if verbose:
            print("All Processes Started")
        i = 0
        data = []
        for proc in procs:
            proc[0].join()
            arr = proc[1]
            data.append((arr[0], arr[1]))
            i += 1
            if verbose:
                print(f"    {i}/{len(procs)}")

        return data

    def _get_mean_squared_error(self, points, slope, intercept):
        """
        _get_mean_squared_error() | gets the mean squared error of a given
            set of points and the equation for a 2D line
        slope     | the slope of the line
        intercept | y_intercept of the line
            y = slope*x + intercept
        returns | (float) mean squared error
        """
        total = 0
        for point in points:
            y1 = slope*point[0] + intercept
            y2 = point[1]

            total += (y2-y1)**2

        return total / len(points)

    def _calculate_best_slope(self, points):
        """
        _calculate_best_slope() | calculates the slope of the lOBF using
            linear regression, for more accurate results the point (0, y)
            should be included
        points | list((float, float)) a set of linear points to
            calculate the slope of
        returns | (int)
        """
        yint = 0
        slope = 0

        # repeat regression 250 times
        for i in range(250):
            # calculate best slope with the given intercept
            max_error = self._get_mean_squared_error(points, slope, yint)
            while True:
                error = self._get_mean_squared_error(points, slope+0.001, yint)
                if error > max_error:
                    break
                slope += 0.001
                max_error = error

            while True:
                error = self._get_mean_squared_error(points, slope-0.001, yint)
                if error > max_error:
                    break
                slope -= 0.0001
                max_error = error

            # calculate best intercept with current slope
            max_error = self._get_mean_squared_error(points, slope, yint)
            while True:
                error = self._get_mean_squared_error(points, slope, yint+0.001)
                if error > max_error:
                    break
                yint += 0.0001
                max_error = error
            while True:
                error = self._get_mean_squared_error(points,
                                                     slope, yint-0.0001)
                if error > max_error:
                    break
                yint -= 0.0001
                max_error = error

        return slope

    def calculate_power(self, start=1, stop=5, inc=0.2, log=False, vis=False):
        """
        calculate_power() | calculates the power of the Fractal using
            Hausdorff's method
        starting_scale  | the starting value to scale the image by
        increase_by     | the amount to increate the scale by each cycle
        number_of_times | the number of times to scale the fractal and count
        log             | (bool) verbose console output
        vis             | (bool) produces visualization of process
        returns | (float) power of the Fractal
        """
        data = self._get_scaling_data_process(start, stop, inc, log)

        logs = []
        for point in data:
            if point[1] == 0:
                return 0
            logs.append((math.log(point[0]), math.log(point[1])))

        if log:
            print("="*12)
            print(data)
            print("="*12)
            print(logs)
            print("="*12)

        power = self._calculate_best_slope(logs)

        if vis:
            fig, (ax1, ax2) = plt.subplots(2, figsize=(11, 7))
            fig.tight_layout(pad=3.0)

            data_x = [x[0] for x in data]
            data_y = [x[1] for x in data]
            logs_x = [x[0] for x in logs]
            logs_y = [x[0] for x in logs]

            ax1.plot(data_x, data_y, "o", color="black")
            ax2.plot(logs_x, logs_y, "o", color="black")
            ax2.plot(logs_x, logs_y)

            ax1.set_title("\"mass\" vs. scaling factor")
            ax2.set_title((
                f"log(\"mass\") vs. log(scaling factor)"
                f" | slope={round(power, 3)}"
            ))

            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png')

            self._power_vis = Image.open(img_buf)

        return power

    def visualize_counting(self):
        """
        visualize_counting() | performs a visualization of the counting method
            used to determine the "mass" of the fractal
        returns | (PIL.Image)
        """
        self._count_non_background_pixels(self._img, generate_image=True)
        return self._vis_img

    def get_last_power_visualization(self):
        """
        get_last_power_visualization() | gets the last visualization
            from Fractal.calculate_power(visualize=True)
        returns | (PIL.Image) if an image is available, None if not
        """

        return self._power_vis

    def set_sample_size(self, size):
        """
        set_sample_size() | changes the grid size used for counting
        size | (int) new grid size
        returns | None
        """
        self._sample_size = size


def get_error_per_fractal(dir):
    """
    get_error_per_fractal() | computes the error for each Fractal and
        returns a list of the best data points for each Fractal in imgs.
        A Fractal is considered the same if it has the same name
    returns | list( (float, float | str) )
    """
    vals = []
    currSet = []

    currentName = None
    files = os.listdir(dir)
    files.append(os.listdir(dir)[0])
    for file in files:
        power, path = file.split(")")
        power = float(power[1::])

        name = " ".join(path.split(".")[:-1])
        if name[-2] == "_":
            name = name[:-2]

        if name != currentName:
            if currentName is not None:
                min = 0
                p = currSet[0][1]
                for i in range(1, len(currSet)):
                    val = currSet[i][0]
                    lowVal = currSet[min][0]
                    print(abs(p-val), abs(lowVal-p), min, p)
                    if abs(power-val) < abs(lowVal-p):
                        min = i

                vals.append(currSet[min])
                print(currSet[min])

                currSet = []
            currentName = name

        print(power, path, currentName)

        f = Fractal(dir + "/" + file)

        p = f.calculate_power()

        currSet.append((p, power, name))
        print(p, power, name)

    return vals


def plot_percent_error_scatter(vals, path):
    """
    plot_percent_error_per_Fractal_scatter() | plots the percent error
        for each fractal given the fractals actual power
        and the predicted value
    vals | list( (predicted_power, actual_power) )
    path | (str) path to save image to ("/path/to/img.png")
    returns | None | saves fig to ts/scraped_data_PIL_error.png
    """

    # compute the percent difference from each value to its actual value
    # as well as the avg percent error for all the Fractals
    perc_errors = []
    actual_powers = []
    avg_error = 0
    for pair in vals:
        diff = abs(pair[0] - pair[1])
        perc_diff = diff/pair[1] * 100
        avg_error += perc_diff
        perc_errors.append(perc_diff)
        actual_powers.append(pair[1])

    avg_error /= len(vals)

    # plot the data as a graph between actual power and percent error
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.tight_layout(pad=3.0)

    ax.plot(actual_powers, perc_errors, "o", color="black")
    ax.plot(actual_powers, [avg_error]*len(vals),
            label=f"Average Error | {round(avg_error,2)}")

    plt.legend(loc='upper center')

    ax.set_title("percent error vs. each power")

    plt.savefig(path)


def plot_percent_error_bar(vals, path):
    """
    plot_percent_error_per_Fractal_scatter() | plots the percent error
        for each fractal given the fractals actual power
        and the predicted value
    vals | list( (predicted_power, actual_power) )
    path | (str) path to save image to ("/path/to/img.png")
    returns | None | saves fig to ts/scraped_data_PIL_error.png
    """

    # compute the percent difference from each value to its actual value
    # as well as the avg percent error for all the Fractals
    perc_errors = []
    names = []
    avg_error = 0
    for pair in vals:
        diff = abs(pair[0] - pair[1])
        perc_diff = diff/pair[1] * 100
        avg_error += perc_diff
        perc_errors.append(perc_diff)
        names.append(pair[2])

    avg_error /= len(vals)

    # plot the data as a graph between actual power and percent error
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.tight_layout(pad=3.0)

    plt.setp(ax.get_xticklabels(), fontsize=6, rotation='45')
    ax.set_ylim(0, 100)

    ax.bar(names, perc_errors)

    ax.set_title(f"percent error per Fractal | avg_error={round(avg_error,2)}")

    plt.savefig(path)


def main():
    # will take ~2.5 hours
    vals = get_error_per_fractal("imgs")
    print("="*12)
    print(vals)
    print("="*12)

    plot_percent_error_scatter(vals, "plts/scraped_data_PIL_error.png")

    # will take ~45 min
    vals = get_error_per_fractal("images/basic_shapes/generated")
    print("="*12)
    print(vals)
    print("="*12)

    plot_percent_error_bar(vals, "plts/generated_polygons.png")

    # other misc images for report

    # power calculation chart
    f = Fractal("test_imgs/circle.png")
    f.calculate_power(visualize=True)
    f.get_last_power_visualization().save("plts/circle_regression.png")

    # counting process chart (small, and big)
    f.visualize_counting().save("plts/counting_circle.png")
    f.set_sample_size(30)
    f.visualize_counting().save("plts/counting_circle_30.png")

    # counting inacuracies image
    f = Fractal("imgs/(1.0)SmithVolterraCantor_set_1.png")
    f.visualize_counting().save("plts/inacurate_counting.png")

    # scaled version of low quality image
    # plus counting errors when scaled
    img = Image.open("images/basic_shapes/generated/(2.0)Circle.png")
    w, h = img.size
    scaleImage(img, (w*5, h*5)).save("plts/scaled_low_quality.png")
    f = Fractal("plts/scaled_low_quality.png")
    f.visualize_counting().save("plts/inacurate_scaled_counting.png")


if "__main__" in __name__:
    main()
