import requests
import re
from serpapi import GoogleSearch


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
    "api_key": "d3c721a310e66cd91398fcad90be734f2158c8f9d0d4fe0761a9671782131124"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    #print(results["images_results"][::8])
    return [image["original"] for image in results["images_results"][:8] if "original" in image]


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

if "__main__" in __name__:
    WIKI_URL = "https://en.wikipedia.org/wiki/List_of_fractals_by_Hausdorff_dimension"
    main()