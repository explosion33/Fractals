import io
import os
import math
from PIL import Image
from multiprocessing import Process, Array, Value
from matplotlib import pyplot as plt
from ImageTools import scaleImage


class Fractal:
    def __init__(self, path) -> None:
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

        # calculate y_intercept
        left_zero = None
        right_zero = None
        at_zero = None
        for point in points:
            if point[0] < 0:
                if left_zero is None or point[0] > left_zero[0]:
                    left_zero = point
            elif point[0] > 0:
                if right_zero is None or point[0] < right_zero[0]:
                    right_zero = point
            else:
                at_zero = point
                break

        y_intercept = at_zero
        if y_intercept is None:
            # TODO implement y-int interpolation
            pass
        else:
            y_intercept = y_intercept[1]

        slope = 0
        max_error = self._get_mean_squared_error(points, slope, y_intercept)
        while True:
            slope += 0.0001
            error = self._get_mean_squared_error(points, slope, y_intercept)
            if error > max_error:
                break
            max_error = error

        while True:
            slope -= 0.0001
            error = self._get_mean_squared_error(points, slope, y_intercept)
            if error > max_error:
                break
            max_error = error

        return slope

    def calculate_power(self, start=1, stop=5, inc=0.2, verbose=False, visualize=False):
        """
        calculate_power() | calculates the power of the Fractal using
            Hausdorff's method
        starting_scale  | the starting value to scale the image by
        increase_by     | the amount to increate the scale by each cycle
        number_of_times | the number of times to scale the fractal and count
        returns | (float) power of the Fractal
        """
        data = self._get_scaling_data_process(start, stop, inc, verbose)

        logs = []
        for point in data:
            if point[1] == 0:
                return 0
            logs.append((math.log(point[0]), math.log(point[1])))

        if verbose:
            print("="*12)
            print(data)
            print("="*12)
            print(logs)
            print("="*12)

        power = self._calculate_best_slope(logs)

        if visualize:
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
            ax2.set_title(f"log(\"mass\") vs. log(scaling factor) slope={round(power, 3)}")

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

def plot_percent_error_per_Fractal_scatter(vals, path):
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
        diff = abs(pair[0]- pair[1])
        perc_diff = diff/pair[1] * 100
        avg_error += perc_diff
        perc_errors.append(perc_diff)
        actual_powers.append(pair[1])
    
    avg_error /= len(vals)

    # plot the data as a graph between actual power and percent error
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.tight_layout(pad=3.0)


    ax.plot(actual_powers, perc_errors, "o", color="black")
    ax.plot(actual_powers, [avg_error]*len(vals), label=f"Average Error | {round(avg_error,2)}")

    plt.legend(loc='upper center')

    ax.set_title("percent error vs. each power")

    plt.savefig(path)

def plot_percent_error_per_Fractal_bar(vals, path):
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
        diff = abs(pair[0]- pair[1])
        perc_diff = diff/pair[1] * 100
        avg_error += perc_diff
        perc_errors.append(perc_diff)
        names.append(pair[2])
    
    avg_error /= len(vals)

    # plot the data as a graph between actual power and percent error
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.tight_layout(pad=3.0)

    plt.setp(ax.get_xticklabels(), fontsize=6, rotation='45')
    ax.set_ylim(0,100)
    
    ax.bar(names, perc_errors)

    ax.set_title(f"percent error per Fractal | avg_error={round(avg_error,2)}")

    plt.savefig(path)


def main():
    # will take ~2.5 hours
    # vals = get_error_per_fractal("imgs")
    # print("="*12)
    # print(vals)
    # print("="*12)


    # data from last computation of data set
    vals = [
        (1.401999999999862, 0.538),
        (1.8437999999998134, 0.6309),
        (1.410499999999861, 0.6942),
        (1.3632999999998663, 0.69897),
        (1.410499999999861, 0.7499),
        (1.5798999999998424, 0.88137),
        (1.5582999999998448, 1.0),
        (1.4733999999998542, 1.0),
        (1.2683999999998767, 1.0),
        (1.4322999999998587, 1.0812),
        (1.7167999999998274, 1.0933),
        (1.6496999999998347, 1.12915),
        (1.2244999999998816, 1.144),
        (1.2782999999998756, 1.2),
        (1.2063999999998836, 1.2083),
        (1.2216999999998819, 1.2108),
        (1.2519999999998785, 1.26),
        (1.3620999999998664, 1.2619),
        (1.4789999999998535, 1.2619),
        (1.2134999999998828, 1.2619),
        (1.956699999999801, 1.2619),
        (1.3944999999998628, 1.2619),
        (1.3315999999998698, 1.2683),
        (1.4777999999998537, 1.3057),
        (1.4972999999998515, 1.328),
        (1.2518999999998786, 1.3934),
        (1.4043999999998618, 1.4649),
        (1.528599999999848, 1.4649),
        (1.5356999999998473, 1.4961),
        (1.6058999999998396, 1.5),
        (1.6039999999998398, 1.5236),
        (1.6039999999998398, 1.5236),
        (1.6220999999998378, 1.585),
        (1.630199999999837, 1.585),
        (1.4712999999998544, 1.585),
        (1.5130999999998498, 1.585),
        (1.3900999999998633, 1.61803),
        (1.2596999999998777, 1.6309),
        (1.5859999999998418, 1.6309),
        (1.6334999999998365, 1.6309),
        (1.6496999999998347, 1.6379),
        (1.5939999999998409, 1.6402),
        (1.2908999999998743, 1.6826),
        (1.5427999999998465, 1.6826),
        (1.792599999999819, 1.699),
        (1.7246999999998265, 1.7),
        (1.78269999999982, 1.7712),
        (1.8487999999998128, 1.7712),
        (1.7597999999998226, 1.7712),
        (1.5882999999998415, 1.7848),
        (1.8666999999998108, 1.8272),
        (1.802399999999818, 1.8617),
        (1.856499999999812, 1.8928),
        (1.7607999999998225, 1.934),
        (1.3327999999998696, 2.0),
        (1.8451999999998132, 2.0),
        (1.4629999999998553, 2.0),
        (1.8894999999998083, 2.0),
        (1.4456999999998572, 2.0),
        (1.8225999999998157, 2.0),
        (1.8087999999998172, 2.0),
        (1.802499999999818, 2.0),
        (1.7638999999998222, 2.0),
        (1.7059999999998285, 2.0),
        (1.6803999999998314, 2.0),
        (1.9425999999998025, 2.0),
        (1.2466999999998791, 2.0),
        (1.3822999999998642, 2.0)
    ]

    plot_percent_error_per_Fractal_scatter(vals, "plts/scraped_data_PIL_error.png")

    # vals = get_error_per_fractal("basic_shapes/generated")
    # print("="*12)
    # print(vals)
    # print("="*12)

    vals =[
        (2.055299999999913, 2.0, 'Arrow 1'),
        (1.9998999999997964, 2.0, 'Arrow 2'),
        (2.0016999999997998, 2.0, 'Circle 2'),
        (2.3745000000005865, 2.0, 'Circle'),
        (1.9950999999997967, 2.0, 'Clover 1'),
        (2.0177999999998337, 2.0, 'Clover 2'),
        (1.9989999999997963, 2.0, 'Crown 1'),
        (1.9900999999997973, 2.0, 'Crown 2'),
        (2.0053999999998076, 2.0, 'Diamond 1'),
        (2.061499999999926, 2.0, 'Diamond 2'),
        (2.009899999999817, 2.0, 'Diamond 3'),
        (2.211300000000242, 2.0, 'Diamond 4'),
        (1.9858999999997977, 2.0, 'Heart 1'),
        (2.0289999999998574, 2.0, 'Heart 2'),
        (1.991399999999797, 2.0, 'Hexagon 1'),
        (2.042499999999886, 2.0, 'Hexagon 2'),
        (2.0063999999998097, 2.0, 'Lightning Bolt 1'),
        (2.047299999999896, 2.0, 'Lightning Bolt 2'),
        (1.9952999999997967, 2.0, 'Moon 1'),
        (1.9905999999997972, 2.0, 'Moon 2'),
        (1.9986999999997963, 2.0, 'Parallelogram 1'),
        (1.9970999999997965, 2.0, 'Parallelogram 2'),
        (2.042199999999885, 2.0, 'Pentagon 1'),
        (2.0029999999998025, 2.0, 'Pentagon 2'),
        (2.2888000000004056, 2.0, 'Rectangle 1'),
        (2.530600000000916, 2.0, 'Rectangle 2'),
        (1.9901999999997972, 2.0, 'Right triangle 1'),
        (1.9954999999997967, 2.0, 'Right Triangle 2'),
        (1.9795999999997984, 2.0, 'Shuriken 1'),
        (1.9995999999997962, 2.0, 'Shuriken 2'),
        (2.2935000000004155, 2.0, 'Speech Bubble 1'),
        (1.9693999999997995, 2.0, 'Speech Bubble 2'),
        (2.272900000000372, 2.0, 'Square 2'),
        (2.515000000000883, 2.0, 'Square'),
        (1.992599999999797, 2.0, 'Trapezoid 1'),
        (2.496100000000843, 2.0, 'Trapezoid 2'),
        (2.383300000000605, 2.0, 'Trapezoid'),
        (2.052999999999908, 2.0, 'Triangle 2'),
        (2.15350000000012, 2.0, 'Triangle')
]

    plot_percent_error_per_Fractal_bar(vals, "plts/generated_polygons.png")

    f = Fractal("test_imgs/circle.png")
    f.calculate_power(visualize=True)
    f.get_last_power_visualization().save("plts/circle_regression.png")

    f.visualize_counting().save("plts/counting_circle.png")
    f.set_sample_size(30)
    f.visualize_counting().save("plts/counting_circle_30.png")

    f = Fractal("imgs/(1.0)SmithVolterraCantor_set_1.png")
    f.visualize_counting().save("plts/inacurate_counting.png")

    img = Image.open("basic_shapes/generated/(2.0)Circle.png")
    w, h = img.size
    scaleImage(img, (w*5, h*5)).save("plts/scaled_low_quality.png")
    f = Fractal("plts/scaled_low_quality.png")
    f.visualize_counting().save("plts/inacurate_scaled_counting.png")





if "__main__" in __name__:
    main()