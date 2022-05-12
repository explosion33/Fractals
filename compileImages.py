import requests
import re


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


WIKI_URL = "https://en.wikipedia.org/wiki/List_of_fractals_by_Hausdorff_dimension"

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



    for fractal in fractals:
        print(fractal)


