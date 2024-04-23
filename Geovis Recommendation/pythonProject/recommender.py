import geodatasets
import numpy as np
import folium
import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import matplotlib.pyplot as plt

from util import is_quantitative, Design

Q = ["_", "SIZE", "COLOR_LIGHTNESS", "COLOR_HUE"]


def recommend_visualisations(
        data: str,
        variables: list,
):
    gpd_data = gpd.read_file(data)

    if not all([var in gpd_data.columns for var in variables]):
        raise ValueError("Invalid column")

    if "geometry" not in gpd_data.columns:
        raise ValueError("Missing geometry column")

    map_designs = []

    for v in variables:
        if is_quantitative(gpd_data, v):
            for q in Q:
                map_designs.append(Design([v], [q]))

    for design in map_designs:
        args = {}

        for i in range(len(design.columns)):
            if design.encodings[i] == "_":
                continue

            if design.encodings[i] == "SIZE":
                args["scale"] = design.columns[i]
                args["limits"] = (4, 20)
                args["edgecolor"] = "black"
                args["color"] = "white"
                args["alpha"] = 0.7
                args["legend"] = True
            elif design.encodings[i] == "COLOR_LIGHTNESS":
                args["hue"] = design.columns[i]
                args["cmap"] = "OrRd"
                args["legend"] = True
                # args["legend_kwargs"] = {"bbox_to_anchor": (0, 0, 0.5, 0.5)}
            elif design.encodings[i] == "COLOR_HUE":
                args["hue"] = design.columns[i]
                args["legend"] = True

        ax = gplt.webmap(gpd_data, projection=gcrs.WebMercator(), figsize=(10, 10))
        gplt.pointplot(gpd_data, ax=ax, **args)

        plt.show()

    return map_designs
