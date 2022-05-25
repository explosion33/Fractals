import requests
import re
import ImageTools
from serpapi import GoogleSearch
import time
from PIL import Image, UnidentifiedImageError
from multiprocessing import Process


def normalize_html(s):
    links = re.findall(r'(<a.*>(.*)<\/a>)', s) # finds all a tags, with a matching group for internal text
    for link in links:
        s = s.replace(link[0], link[1])

    spans = re.sub(r'(<span.*?>(.*<\/span>){0,1})', "", s) # finds all span tags

    return s

def normalize_float(s):
    s = re.sub(r'<.*>', "", s) # removes any html segments
    s = re.sub(r'±.*', "", s) # removes any uncertainity measures
    s = re.sub(r'(?:[^\d.]|\.\.\.)', "", s) # removes any remaining non-number characters and ...

    try:
        return float(s)
    except(ValueError):
        return None

def parse_image_html(s):

    match = re.search(r'<img.*src="(.*?)"', s)

    if match is None:
        return match

    return "https:" + match.group(1)

def get_image_from_url(url):
    if url is None:
        return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" }
    res = None
    try:
        res = requests.get(url, stream=True, headers=headers)
    except:
        res = requests.get(url, stream=True, verify=False, headers=headers)

    if res.status_code == 200:
        try:
            return Image.open(res.raw)
        except(UnidentifiedImageError):
            return None

    print(res.status_code, url)
    return None

def get_alternative_images(name):
    name += " HD fractal"

    print("="*20)
    print(name)
    print("="*20)

    params = {
    "engine": "google",
    "ijn": "0",
    "q": name,
    "google_domain": "google.com",
    "tbm": "isch",
    "api_key": "56c62a554bf4164832a616e8257bd35446e610c4322ebc37a6a42cd5cdf5c10f"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    return [image["original"] for image in results["images_results"][:8] if "original" in image]

def format_file_name(name):
    name = re.sub(r'[^\da-zA-Z_ ]', "", name)
    name = "_".join(name.split())
    return name


def main():
    res = requests.get(WIKI_URL)

    if res.status_code == 200:
        html = res.text

        match = re.findall(r'<tr>\n[\s\S\n]*?<\/td>\n.*?>(.*)<\/td>\n<td>(.*)<.*\n(.*)', html)

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
                print(fractal)
                f.write(str(fractal))
                f.write("\n")

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
                        img.save("imgs/(" + str(power) + ")" + name + "_" + str(i) + ".png")
                        i += 1



                

        

if "__main__" in __name__:
    WIKI_URL = "https://en.wikipedia.org/wiki/List_of_fractals_by_Hausdorff_dimension"
    main()