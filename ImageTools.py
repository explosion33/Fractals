from PIL import Image


def scaleImage(img, new_size, keep_aspect_ratio=False):
    """
    scaleImaeg() | scales the provided image to the provided resolution
    img | PIL image object
    new_size | (width, height)
    keep_aspect_ratio | (bool) (default = False), if True adjusts
        provided height to maintain original aspect ratio

    returns | scaled image
    """
    w, h = new_size
    w = int(w)
    h = int(h)
    new_size = (w, h)

    if not keep_aspect_ratio:
        return img.resize(new_size, Image.ANTIALIAS)

    oldW = img.size[0]
    ratio = w / oldW
    newH = int(ratio * img.size[1])

    return img.resize((w, newH), Image.ANTIALIAS)


def check_similarity(img1, img2):
    """
    check_similarity() | checks the similarity between two PIL images
    img1 | first PIL Image object
    img2 | second PIL Image object

    returns | (float) 0 to 1, 1 being a 100% match and 0 being a 0% match
    """
    # get raw pixel data of each image
    d1 = list(img1.getdata())
    d2 = list(img2.getdata())

    # find the large of the two images
    large = d1 if len(d1) > len(d2) else d2
    small = d1 if large is d2 else d2

    # compute difference between the images
    total = len(large)
    error = len(large) - len(small)  # error based on dimensions

    for i in range(len(small)):
        p1 = large[i]
        p2 = small[i]

        if p1 != p2:
            error += 1

    return 1 - (error / total)


def to_mono(img):
    return img.convert("1")


if "__main__" in __name__:
    img = Image.open("test_imgs/Crown.png")
    to_mono(img).show()
