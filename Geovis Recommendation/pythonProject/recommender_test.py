import unittest
import geopandas as gpd
import numpy as np

from recommender import recommend_visualisations, enumerate_designs, filter_out_invalid_designs
from util import Design, Encoding, Design2, Q, C


class TestRecommender(unittest.TestCase):
    def test_missing_geometry_column(self):
        bean_density = gpd.read_file("bean_density.geojson")
        bean_density[["MBPA_Tot_H"]].to_file('clean_bean_density.geojson', driver='GeoJSON')

        with self.assertRaises(ValueError):
            recommend_visualisations("./clean_bean_density.geojson", ["MBPA_Tot_H"])

    def test_invalid_column(self):
        with self.assertRaises(ValueError):
            recommend_visualisations("./bean_density.geojson", ["invalid_column"])

    def test_enumerate_designs(self):
        ng_water_points = gpd.read_file("test_nigeria_water_points.geojson")
        actual = enumerate_designs(variables=["water_type", "water_quantity"], gpd_data=ng_water_points)
        actual = filter_out_invalid_designs(actual)
        # print(actual)
        for d in actual:
            print(d)

    def test_design_get_kwargs(self):
        e1 = Encoding("water_type", C.COLOR_HUE_C)
        e2 = Encoding("water_quantity", Q.SIZE)
        d = Design2([e1, e2])

        print(d.get_kwargs())

    def test__(self):
        recommend_visualisations("./test_nigeria_water_points.geojson", ["water_type", "households_served"])
