import math
from turtle import left
from PIL import Image
from ImageTools import scaleImage

class Fractal:
    def __init__(self, path) -> None:
        self._img = Image.open(path)
        self._sample_size = 2

        self._vis_img = None

        self._OVERLAY_COLOR = (255,255,0,100)

    def _get_background_color(self, img):
        """
        _get_background_color() | gets the background color of an image
            using the assumption that the background color is the most occuring color
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

    def _count_non_background_pixels(self, img, generate_image = False):
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
                indexes = self._get_square_indicies(img, x,y)
                
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
                            #if data[w*(py) + (px)] == bckg:
                            pixel = self._vis_img.getpixel((px,py))
                            alpha = self._OVERLAY_COLOR[3]

                            # mix overlay color with image base color
                            R = int((pixel[0]*(255-alpha) + 
                                    self._OVERLAY_COLOR[0]*alpha)/255)
                            G = int((pixel[1]*(255-alpha) + 
                                    self._OVERLAY_COLOR[1]*alpha)/255)
                            B = int((pixel[2]*(255-alpha) + 
                                    self._OVERLAY_COLOR[2]*alpha)/255)

                            mixed = (R, G, B, 255)
                            self._vis_img.putpixel((px,py), mixed) 
        return count

    def _get_scaling_data(self, inc, times, curr_factor=1, points=[]):
        """
        _get_scaling_data() | performs the scale up / count pixels operation
            for the specified amount of scales
        inc         | (float) amount to increment each subsequent scale by
        times       | (int) number of times to scale
        curr_factor | (float) (default=1) the scaling factor to start at
        points      | list((float,float)) (default=[]) list of points
            to append to
        returns | list((float,float)) list of points (scaling factor, #pixels)
        """
        if times == 5:
            print(points)
        if times <= 0:
            return points
        
        w, h = self._img.size
        scaledImg = scaleImage(self._img, (w*curr_factor, h*curr_factor))
        count = self._count_non_background_pixels(scaledImg)
        points.append((curr_factor, count))

        return self._get_scaling_data(inc, times-1, curr_factor+inc, points)

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
        
        return total / len(point)

    def _calculate_best_slope(self, points):
        """
        _calculate_best_slope() | calculates the slope of the lOBF using
            linear regression, for more accurate results the point (0, y)
            should be included
        points | list((float, float)) a set of linear points to
            calculate the slope of
        returns | (int)
        """
        
        #calculate y_intercept
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
            pass #TODO implement y-int interpolation
        else:
            y_intercept = y_intercept[1]


        slope = 0
        max_error = self._get_mean_squared_error(points, slope, y_intercept)
        while True:
            slope += 0.01
            error = self._get_mean_squared_error(points, slope, y_intercept)
            if error > max_error:
                break
            max_error = error

        while True:
            slope -= 0.01
            error = self._get_mean_squared_error(points, slope, y_intercept)
            if error > max_error:
                break
            max_error = error

        print(y_intercept)
        return slope
        
    def calculate_power(self, starting_scale=0.6, increase_by=0.2, number_of_times=15):
        """
        calculate_power() | calculates the power of the Fractal using
            Hausdorff's method
        starting_scale  | the starting value to scale the image by
        increase_by     | the amount to increate the scale by each cycle
        number_of_times | the number of times to scale the fractal and count
        returns | (float) power of the Fractal
        """
        data = self._get_scaling_data(increase_by, number_of_times, increase_by, [])

        logs = []
        for point in data:
            logs.append((math.log(point[0]), math.log(point[1])))

        print(data, logs)

        power = self._calculate_best_slope(logs)
        return power

    def visualize_counting(self):
        """
        visualize_counting() | performs a visualization of the counting method
            used to determine the "mass" of the fractal
        returns | (PIL.Image)
        """
        self._count_non_background_pixels(self._img, generate_image = True)
        return self._vis_img


if "__main__" in __name__:
    paths = ["(1.585)Sierpiski.png", "(2.0)test1.png", "circle.png"]#, "(2.0)test2.png", "(0.5)test3.png"]


    for path in paths:
        f = Fractal(path)

        print(f.calculate_power())
        f.visualize_counting().show()