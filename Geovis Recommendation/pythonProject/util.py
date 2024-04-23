import numpy as np


class Design():
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