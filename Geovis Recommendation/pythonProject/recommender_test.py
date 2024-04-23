import unittest
import geopandas as gpd

from recommender import recommend_visualisations


class TestRecommender(unittest.TestCase):
    def test_missing_geometry_column(self):
        bean_density = gpd.read_file("bean_density.geojson")
        bean_density[["MBPA_Tot_H"]].to_file('clean_bean_density.geojson', driver='GeoJSON')

        with self.assertRaises(ValueError):
            recommend_visualisations("./clean_bean_density.geojson", ["MBPA_Tot_H"])


    def test_invalid_column(self):
        with self.assertRaises(ValueError):
            recommend_visualisations("./bean_density.geojson", ["invalid_column"])


