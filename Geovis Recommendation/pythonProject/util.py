from dataclasses import dataclass
from enum import StrEnum

import numpy as np
import geoplot as gplt
import geoplot.crs as gcrs
import matplotlib as mpl


class Q(StrEnum):
    NONE = "_"
    SIZE = "SIZE"
    COLOR_LIGHTNESS_H = "COLOR_LIGHTNESS_H"
    COLOR_LIGHTNESS_L = "COLOR_LIGHTNESS_L"
    COLOR_HUE = "COLOR_HUE"


class C(StrEnum):
    NONE = "_"
    COLOR_HUE_C = "COLOR_HUE_C"
    SHAPE = "SHAPE"


class Intents(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"
    MAGNITUDE = "MAGNITUDE"


@dataclass()
class VarIntent:
    variable: str
    intent: Intents


@dataclass(frozen=True)
class Encoding:
    variable: str
    encoding: str

    def get_kwargs(self):
        if self.encoding == Q.NONE or self.encoding == C.NONE:
            return {"edgecolor": "white", "s": 7, "alpha": 0.8}
        elif self.encoding == Q.SIZE:
            return {
                "scale": self.variable,
                "limits": (4, 20),
                "edgecolor": "black",
                "color": "white",
                "alpha": 0.7,
                "legend": True
            }
        elif self.encoding == Q.COLOR_LIGHTNESS_H:
            return {"hue": self.variable, "cmap": "Blues", "edgecolor": "white", "linewidth": 0.5, "s": 10, "alpha": 0.8,
                    "legend": True, "legend_kwargs": {"shrink": 0.5}}
        elif self.encoding == Q.COLOR_LIGHTNESS_L:
            return {"hue": self.variable, "cmap": "Blues_r", "edgecolor": "white", "linewidth": 0.5, "s": 10,
                    "alpha": 0.8, "legend": True, "legend_kwargs": {"shrink": 0.5}}
        elif self.encoding == Q.COLOR_HUE:
            return {"hue": self.variable, "edgecolor": "white", "linewidth": 0.5, "alpha": 0.8, "s": 10,
                    "legend": True, "legend_kwargs": {"shrink": 0.5}}
        elif self.encoding == C.COLOR_HUE_C:
            return {"hue": self.variable, "cmap": "tab10", "legend": True, "s": 10, "alpha": 0.8, "edgecolor": "white",
                    "linewidth": 0.5}
        elif self.encoding == C.SHAPE:
            return {}

    def msg(self):
        if self.encoding == Q.SIZE:
            return f"Magnitude of `{self.variable}` (Size)"
        elif self.encoding == Q.COLOR_LIGHTNESS_H:
            return f"Highest `{self.variable}` (C-Intensity)"
        elif self.encoding == Q.COLOR_LIGHTNESS_L:
            return f"Lowest `{self.variable}` (C-Intensity)"
        elif self.encoding == Q.COLOR_HUE:
            return f"Magnitude of `{self.variable}` (C-Hue)"
        elif self.encoding == C.COLOR_HUE_C:
            return f"Category of {self.variable} (C-Hue)"
        elif self.encoding == C.SHAPE:
            return f"Category of {self.variable} (Shape)"

    def score(self, intent: VarIntent = None):
        if self.encoding == Q.SIZE:
            return 5
        elif self.encoding == Q.COLOR_LIGHTNESS_H:
            return 10 if intent is not None and intent.intent == Intents.HIGH else 3
        elif self.encoding == Q.COLOR_LIGHTNESS_L:
            return 10 if intent is not None and intent.intent == Intents.LOW else 3
        elif self.encoding == Q.COLOR_HUE:
            return 10 if intent is not None and intent.intent == Intents.MAGNITUDE else 4

        elif self.encoding == C.COLOR_HUE_C:
            return 10
        elif self.encoding == C.SHAPE:
            return 5


@dataclass(frozen=True)
class Design2:
    encodings: list[Encoding]

    def __hash__(self):
        return hash(tuple(self.encodings))

    def score(self, intent: VarIntent = None):
        return sum([e.score(intent) for e in self.encodings])

    def add_encoding(self, encoding):
        if not isinstance(encoding, Encoding):
            raise ValueError("Can only add Encoding objects")

        es = self.encodings + [encoding]
        es = sorted(es, key=lambda e: e.variable)

        return Design2(es)

    def is_valid(self):
        for i in range(len(self.encodings) - 1):
            v, e = self.encodings[i].variable, self.encodings[i].encoding
            for j in range(i + 1, len(self.encodings)):
                if self.encodings[j].variable == v or self.encodings[j].encoding == e:
                    return False
                has_color = (
                        e == Q.COLOR_HUE or e == Q.COLOR_LIGHTNESS_H or e == Q.COLOR_LIGHTNESS_L or e == C.COLOR_HUE_C)
                other_has_color = (self.encodings[j].encoding == Q.COLOR_HUE or self.encodings[
                    j].encoding == Q.COLOR_LIGHTNESS_H or
                                   self.encodings[j].encoding == Q.COLOR_LIGHTNESS_L or self.encodings[
                                       j].encoding == C.COLOR_HUE_C)
                if has_color and other_has_color:
                    return False

        return True

    def get_kwargs(self):
        kwargs = {}
        for encoding in self.encodings:
            kwargs.update(encoding.get_kwargs())
        return kwargs

    def has_encoding(self, encoding):
        return encoding in [e.encoding for e in self.encodings]

    def has_variable(self, variable):
        return variable in [e.variable for e in self.encodings]

    def msg(self):
        return "; ".join([e.msg() for e in self.encodings])

    def plot(self, gpd_data, figsize=(10, 10)):
        print("Plotting", self)
        ax = gplt.webmap(gpd_data, projection=gcrs.WebMercator(), figsize=figsize,
                         extent=relax_bounds(*gpd_data.total_bounds))
        ax.set_title(self.msg() + f" (Score: {self.score()})")

        if self.has_encoding(C.SHAPE):
            column = [e.variable for e in self.encodings if e.encoding == C.SHAPE][0]

            if self.has_encoding(Q.SIZE):
                args = {"edgecolor": "white", "linewidth": 0.5}
            else:
                args = {"s": 10, "edgecolor": "white", "linewidth": 0.5}

            if self.has_encoding(Q.COLOR_HUE):
                c_hue_col = [e.variable for e in self.encodings if e.encoding == Q.COLOR_HUE][0]
                args["norm"] = mpl.colors.Normalize(vmin=gpd_data[c_hue_col].min(), vmax=gpd_data[c_hue_col].max())
            elif self.has_encoding(Q.COLOR_LIGHTNESS_H):
                c_l_hue_col = [e.variable for e in self.encodings if e.encoding == Q.COLOR_LIGHTNESS_H][0]
                args["norm"] = mpl.colors.Normalize(vmin=gpd_data[c_l_hue_col].min(), vmax=gpd_data[c_l_hue_col].max())
            elif self.has_encoding(Q.COLOR_LIGHTNESS_L):
                c_l_hue_col = [e.variable for e in self.encodings if e.encoding == Q.COLOR_LIGHTNESS_L][0]
                args["norm"] = mpl.colors.Normalize(vmin=gpd_data[c_l_hue_col].min(), vmax=gpd_data[c_l_hue_col].max())
            elif self.has_encoding(C.COLOR_HUE_C):
                c_hue_col = [e.variable for e in self.encodings if e.encoding == C.COLOR_HUE_C][0]
                args["norm"] = mpl.colors.Normalize(vmin=gpd_data[c_hue_col].min(), vmax=gpd_data[c_hue_col].max())

            if self.has_encoding(Q.SIZE):
                size_col = [e.variable for e in self.encodings if e.encoding == Q.SIZE][0]
                args["scale_func"] = lambda minval, maxval: lambda val: np.interp(val, (
                    gpd_data[size_col].min(), gpd_data[size_col].max()), (4, 20))

            args.update(self.get_kwargs())

            if "scale" in args and "s" in args:
                args.pop("s")

            if "hue" in args and "color" in args:
                args.pop("color")

            markers = ["o", "D", "^", "v", "s", "X", "P", "d"]
            unique_values = gpd_data[column].unique()

            for i in range(len(unique_values)):
                if i > 0:
                    if "legend" in args:
                        args.pop("legend")
                    if "legend_kwargs" in args:
                        args.pop("legend_kwargs")

                gplt.pointplot(
                    gpd_data[gpd_data[column] == unique_values[i]],
                    projection=gplt.crs.WebMercator(),
                    ax=ax, marker=markers[i],
                    label=unique_values[i],
                    extent=relax_bounds(*gpd_data.total_bounds),
                    # norm=mpl.colors.Normalize(vmin=gpd_data[
                    # edgecolor='white', linewidth=0.5,
                    # s=10,
                    **args
                )
            ax.legend()
        else:
            args = self.get_kwargs()
            if "scale" in args and "s" in args:
                args.pop("s")

            if "hue" in args and "color" in args:
                args.pop("color")

            # print("Args", args)
            gplt.pointplot(gpd_data, ax=ax, **args)


class Design:
    def __init__(self, columns, encodings):
        self.columns = columns
        self.encodings = encodings

    def __str__(self):
        return f"{self.columns} : {self.encodings}"

    def __repr__(self):
        return f'<Design {self.columns}: {self.encodings}>'


def is_quantitative(gpd_data, column):
    column_dtype = gpd_data.dtypes[column]
    if column_dtype == np.float64 or column_dtype == np.int64:
        return True

    return False


def is_categorical(gpd_data, column):
    column_dtype = gpd_data.dtypes[column]
    if column_dtype == "object":
        return True

    return False


def relax_bounds(xmin, ymin, xmax, ymax):
    """
    Increases the viewport slightly. Used to ameliorate plot features that fall out of bounds.
    """
    window_resize_val_x = 0.1 * (xmax - xmin)
    window_resize_val_y = 0.1 * (ymax - ymin)
    extrema = np.array([
        np.max([-180, xmin - window_resize_val_x]),
        np.max([-90, ymin - window_resize_val_y]),
        np.min([180, xmax + window_resize_val_x]),
        np.min([90, ymax + window_resize_val_y])
    ])
    return extrema
