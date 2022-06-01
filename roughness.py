import os
from matplotlib import pyplot as plt
from Fractal import Fractal
import geopandas as gpd


def get_state_roughness(dir):
    vals = []
    for file in os.listdir(dir):
        path = dir + "/" + file

        name = file.split("-")[0]

        print(name)

        f = Fractal(path)
        power = f.calculate_power(0.5, 2.6, 0.3, log=True)
        print(name, power)

        vals.append((name, power))
    return vals


def plot_state_roughness(powers, path):
    df = gpd.read_file(USA_GEO)

    df["power"] = 0
    for pair in powers:
        state = pair[0]
        power = pair[1]

        i = df.index[df["NAME"] == state][0]
        df.at[i, "power"] = power

    fig, ax = plt.subplots(1, figsize=(11, 7))

    df = df[(df['NAME'] != 'Alaska') & (df['NAME'] != 'Hawaii') &
            (df["NAME"] != 'Puerto Rico')]
    df.plot(column="power", vmin=1.8, vmax=1.9, legend=True)

    plt.title("Border Smoothness per State")
    plt.axis("off")
    plt.savefig(path)


def main():
    # takes about 40 minutes
    vals = get_state_roughness("state_borders")
    print("="*20)
    print(vals)
    print("="*20)

    plot_state_roughness(vals, "plts/state_roughness.png")


if "__main__" in __name__:
    USA_GEO = "gz_2010_us_040_00_5m.json"
    main()
