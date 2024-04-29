import numpy as np
import geopandas as gpd
from shapely import Polygon


def is_crowded(points_grid, data, k=50, threshold=0.25):
    collisions_grid = points_grid - 1
    crowded_cells = collisions_grid[collisions_grid > k]

    collision_points_ratio = crowded_cells.sum() / len(data)

    return collision_points_ratio > threshold


def compute_crowding_ratio(
        points: gpd.GeoDataFrame,
        figsize: tuple,
        s: float = 7,
        k: int = 50,
        threshold: float = 0.25,
):
    points_grid = compute_point_distribution_grid(points, figsize, s)

    collisions_grid = points_grid - 1
    crowded_cells = collisions_grid[collisions_grid > k]

    crowded_points_ratio = crowded_cells.sum() / len(points)

    return crowded_points_ratio, crowded_points_ratio > threshold


def compute_point_distribution_grid(
        points: gpd.GeoDataFrame,
        figsize: tuple,
        s: float = 7,
):
    point_size = s * (1 / 72)  # Convert points to inches
    grid_cell_size = point_size
    bounds = points.total_bounds

    c_width = bounds[2] - bounds[0]
    c_height = bounds[3] - bounds[1]

    i_width = figsize[0]
    i_height = figsize[1]

    c_width_ratio = c_width / i_width
    c_height_ratio = c_height / i_height

    x = points.geometry.x
    y = points.geometry.y
    x = (x - bounds[0]) / c_width_ratio
    y = (y - bounds[1]) / c_height_ratio

    rescaled_data = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x, y))

    num_cells = np.ceil([i_height / grid_cell_size, i_width / grid_cell_size]).astype(int)
    cells = np.zeros(num_cells).astype(int)

    for row in range(num_cells[0]):
        for col in range(num_cells[1]):
            x_min = col * grid_cell_size
            x_max = (col + 1) * grid_cell_size
            y_min = row * grid_cell_size
            y_max = (row + 1) * grid_cell_size

            grid_cell = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
            cells[row, col] = np.sum(rescaled_data.geometry.intersects(grid_cell))

    return cells
