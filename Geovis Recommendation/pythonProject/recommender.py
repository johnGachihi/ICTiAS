import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import itertools

from matplotlib import pyplot as plt

from util import is_quantitative, Design, is_categorical, Design2, Encoding, VarIntent

# Q = ["_", "SIZE", "COLOR_LIGHTNESS_H", "COLOR_LIGHTNESS_L", "COLOR_HUE"]
# C = ["_", "SHAPE", "COLOR_HUE_C"]
Q = ["SIZE", "COLOR_LIGHTNESS_H", "COLOR_LIGHTNESS_L", "COLOR_HUE"]
C = ["SHAPE", "COLOR_HUE_C"]


def recommend_visualisations(
        data: str,
        variables: list,
        filter: list = None,
        intent: VarIntent = None,
        rank: bool = False,
        figsize=(10, 10)
):
    gpd_data = gpd.read_file(data)

    for v in variables:
        if v not in gpd_data.columns:
            raise ValueError(f"Invalid column: {v}")

    if "geometry" not in gpd_data.columns:
        raise ValueError("Missing geometry column")

    map_designs = []

    for v in variables:
        if is_quantitative(gpd_data, v):
            for q in Q:
                map_designs.append(Design([v], [q]))
        elif is_categorical(gpd_data, v):
            for c in C:
                map_designs.append(Design([v], [c]))

    map_designs_2 = enumerate_designs(variables, gpd_data)
    map_designs_2 = filter_out_invalid_designs(map_designs_2)
    map_designs_2 = filter_by_user_preferences(map_designs_2, filter)
    if rank:
        map_designs_2 = order_by_score(map_designs_2, intent)

    # for d in map_designs_2:
        # print(d)
        # pass

    for design in map_designs_2:
        design.plot(gpd_data, figsize=figsize)
        plt.show()

    # for design in map_designs:
    #     ax = gplt.webmap(gpd_data, projection=gcrs.WebMercator(), figsize=(10, 10))
    #     ax.set_title(str(design))
    #     args = {}
    #
    #     for i in range(len(design.columns)):
    #         if design.encodings[i] == "_":
    #             args["edgecolor"] = "white"
    #             args["s"] = 7
    #             args["alpha"] = 0.8
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "SIZE":
    #             args["scale"] = design.columns[i]
    #             args["limits"] = (4, 20)
    #             args["edgecolor"] = "black"
    #             args["color"] = "white"
    #             args["alpha"] = 0.7
    #             args["legend"] = True
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "COLOR_LIGHTNESS_H":
    #             args["hue"] = design.columns[i]
    #             args["cmap"] = "Blues"
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "COLOR_LIGHTNESS_L":
    #             args["hue"] = design.columns[i]
    #             args["cmap"] = "Blues_r"
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "COLOR_HUE_C":
    #             args["hue"] = design.columns[i]
    #             args["cmap"] = "tab10"
    #             args["legend"] = True
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "COLOR_HUE":
    #             args["hue"] = design.columns[i]
    #             args["legend"] = True
    #
    #             gplt.pointplot(gpd_data, ax=ax, **args)
    #         elif design.encodings[i] == "SHAPE":
    #             column = design.columns[i]
    #             markers = ["o", "D", "^", "P", "s", "X", "v", "d"]
    #             unique_values = gpd_data[column].unique()
    #             print(unique_values)
    #
    #             for i in range(len(unique_values)):
    #                 gplt.pointplot(
    #                     gpd_data[gpd_data[column] == unique_values[i]],
    #                     projection=gplt.crs.WebMercator(),
    #                     ax=ax, marker=markers[i], label=unique_values[i],
    #                     edgecolor='white', linewidth=0.5, s=10,
    #                 )
    #             ax.legend()
    #
    #     # gplt.pointplot(gpd_data, ax=ax, **args)
    #
    #     # plt.show()

    return map_designs


def enumerate_designs(variables, gpd_data):
    designs = []

    Vq, Vc = split_into_Q_and_C_vars(variables, gpd_data)

    # Primitive encodings
    M = [Encoding(v, k)
         for v, k in list(itertools.product(Vc, C)) + list(itertools.product(Vq, Q))]
    # print("M", M)

    designs.extend([Design2([m]) for m in M])

    last_added = designs.copy()

    for i in range(2):
        new_designs = []
        for j in range(len(last_added)):
            for m in M:
                new_designs.append(last_added[j].add_encoding(m))

        designs.extend(new_designs)
        last_added = new_designs

    return designs


def filter_out_invalid_designs(map_designs_2):
    map_designs_2 = remove_duplicates(map_designs_2)
    return [d for d in map_designs_2 if d.is_valid()]


def remove_duplicates(input_list):
    result = []
    [result.append(i) for i in input_list if i not in result]
    return result


def split_into_Q_and_C_vars(variables, gpd_data):
    Vc, Vq = [], []
    for v in variables:
        if is_quantitative(gpd_data, v):
            Vq.append(v)
        elif is_categorical(gpd_data, v):
            Vc.append(v)

    return Vq, Vc


def filter_by_user_preferences(designs: list[Design2], filter: list = None):
    if not filter:
        return designs

    result = []

    for d in designs:
        if all([d.has_variable(f) for f in filter]):
            result.append(d)

    return result


def order_by_score(designs: list[Design2], intent=None):
    return sorted(designs, key=lambda d: d.score(intent), reverse=True)
