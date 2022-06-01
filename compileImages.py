"""
Ethan Armstrong
Section AD

This module provides a variety of functions for
    scraping web data
    parsing html
    normalizing html
    searching google
    downloading and saving images
"""

import requests
import re
import ImageTools
from serpapi import GoogleSearch
from PIL import Image, UnidentifiedImageError


def normalize_html(text):
    """
    normalize_html() | removes <a> </a> tags from around links,
        and removes span tags
    text | (str) text to be normalized
    returns | (str)
    """
    # finds all a tags, with a matching group for internal text
    links = re.findall(r'(<a.*>(.*)<\/a>)', text)
    for link in links:
        text = text.replace(link[0], link[1])

    # finds all span tags
    text = re.sub(r'(<span.*?>(.*<\/span>){0,1})', "", text)

    return text


def normalize_float(s):
    """
    normalize_float() | extracts a float from a string that may contain html
        removes tags
        removes special characters
        removes non number characters
    s | (str) text containing a float
    returns | (float) if a valid float exits, None otherwise
    """
    s = s.strip()
    # removes any html segments
    s = re.sub(r'<.*>', "", s)
    # removes any uncertainity measures
    s = re.sub(r'±.*', "", s)
    # removes any remaining non-number characters and "..."
    s = re.sub(r'(?:[^\d.]|\.\.\.)', "", s)

    try:
        return float(s)
    except(ValueError):
        return None


def parse_image_html(s):
    """
    parse_image_html() | gets the URL for an image contained within
        an html segment
    s | (str) text containing an html image
    returns | (str) if an image link was found, None otherwise
    """
    match = re.search(r'<img.*src="(.*?)"', s)

    if match is None:
        return None

    return "https:" + match.group(1)


def get_image_from_url(url):
    """
    get_image_from_url() | downloads an image from the internet given its url
    url | the url of the iamge to be downloaded
    returns | (PIL.Image) if the Image could be downloaded, None if not
    """
    if url is None:
        return None

    # disguise as actual user to avoid Forbidden response
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0)"
                       "Gecko/20100101 Firefox/100.0")
    }

    # get a response via https, if that fails
    # (the site it http, or invalid cert), try without verifying
    res = None
    try:
        res = requests.get(url, stream=True, headers=headers)
    except(requests.Timeout):
        res = requests.get(url, stream=True, verify=False, headers=headers)

    if res.status_code == 200:
        try:
            return Image.open(res.raw)
        except(UnidentifiedImageError):
            return None

    print(res.status_code, url)
    return None


def get_alternative_images(name):
    """
    get_alternative_images() | gets alternative images from google given
        the image name
    returns | list( (str) ) list of links to the alternative images
    """
    name += " HD fractal"

    print("="*20)
    print(name)
    print("="*20)

    API = "56c62a554bf4164832a616e8257bd35446e610c4322ebc37a6a42cd5cdf5c10f"
    params = {
        "engine": "google",
        "ijn": "0",
        "q": name,
        "google_domain": "google.com",
        "tbm": "isch",
        "api_key": API
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    first8 = results["images_results"][:8]
    return [image["original"] for image in first8 if "original" in image]


def format_file_name(name):
    """
    format_file_name() | removes all characters that cannot be in a file
    name | (str) the name of the file
    returns | (str) formatted file name
    """
    name = re.sub(r'[^\da-zA-Z_ ]', "", name)
    name = "_".join(name.split())
    return name


def main():
    res = requests.get(WIKI_URL)

    if res.status_code == 200:
        html = res.text

        # matches the fractal name, power and image list
        pat = r'<tr>\n[\s\S\n]*?<\/td>\n.*?>(.*)<\/td>\n<td>(.*)<.*\n(.*)'
        match = re.findall(pat, html)

        # gets data and normalizes text
        fractals = []
        for i in range(len(match)):
            m = match[i]

            power = normalize_float(m[0])

            if power is not None:
                name = normalize_html(m[1])
                image = parse_image_html(m[2])
                fractals.append((name, power, image))

        with open("results.txt", "w", encoding="utf-8") as f:
            for fractal in fractals:
                # write name, power, link to file
                print(fractal)
                f.write(str(fractal))
                f.write("\n")

                # write alt links to file
                alts = get_alternative_images(fractal[0])
                for alt in alts:
                    f.write("\t")
                    f.write(alt)
                    f.write("\n")

                # save to folder
                name, power, link = fractal

                name = format_file_name(name)

                img = get_image_from_url(link)
                if img is not None:
                    img = ImageTools.to_mono(img)
                    img.save("imgs/(" + str(power) + ")" + name + ".png")

                i = 1
                for link in alts:
                    img = get_image_from_url(link)
                    if img is not None:
                        img = ImageTools.to_mono(img)
                        img.save(f"imgs/({power}){name}_{i}.png")
                        i += 1


if "__main__" in __name__:
    WIKI_URL = (
        "https://en.wikipedia.org/"
        "wiki/List_of_fractals_by_Hausdorff_dimension"
    )
    main()
