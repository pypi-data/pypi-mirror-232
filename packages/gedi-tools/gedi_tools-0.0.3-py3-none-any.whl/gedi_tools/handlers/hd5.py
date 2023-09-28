import warnings

import h5py
import pandas as pd
import numpy as np
from tqdm import tqdm

from gedi_tools.classes.l2b import L2B


class GediTransformer:
    """
    A transformer class for converting GEDI HDF5 data to L2B format.

    This class provides methods for transforming GEDI data stored in HDF5 files into L2B objects.
    The conversion can be done for a single HDF5 file or a list of HDF5 files. Optionally, a GeoDataFrame
    can be provided for clipping the data.

    Attributes:
        None

    Example:
        >>> transformer = GediTransformer()
        >>> l2b_single = GediTransformer.hd5_to_l2b("path/to/hd5_file.hd5")
        >>> l2b_multiple = GediTransformer.hd5_list_to_l2b(["path1.hd5", "path2.hd5"], clip_gdf=some_shape)
    """
    @staticmethod
    def _add_or_update_nested_item(dictionary, key, nested_key, value):
        """
        Adds or updates a nested item within a dictionary.

        Args:
            dictionary (dict): The dictionary to update.
            key (str): The key for the outer dictionary.
            nested_key (str): The key for the inner dictionary.
            value: The value to set or update.

        Raises:
            TypeError: If the types of the existing and new values are incompatible.

        Example:
            >>> d = {}
            >>> GediTransformer._add_or_update_nested_item(d, 'outer', 'inner', 1)
            >>> print(d)
            {'outer': {'inner': 1}}
        """
        dictionary.setdefault(key, {})
        if nested_key not in dictionary[key]:
            dictionary[key][nested_key] = value
        else:
            if isinstance(dictionary[key][nested_key], list) and isinstance(value, list):
                dictionary[key][nested_key].extend(value)
            elif isinstance(dictionary[key][nested_key], int) and isinstance(value, int):
                dictionary[key][nested_key] += value
            else:
                raise TypeError("Incompatible types")

    @classmethod
    def hd5_to_l2b(cls, hd5_file):
        """
        Converts an HDF5 file to an L2B object.

        Args:
            hd5_file (str): The path to the HDF5 file.

        Returns:
            L2B: An L2B object containing the converted data.

        Example:
            >>> l2b_data = GediTransformer.hd5_to_l2b("path/to/hd5_file.hd5")
            >>> print(type(l2b_data))
            <class 'gedi_tools.classes.l2b.L2B'>
        """
        gedi_l2b = h5py.File(hd5_file, 'r')
        gedi_l2b_objs = []
        gedi_l2b.visit(gedi_l2b_objs.append)
        pgap_theta_z_data = []
        gedi_sds = [o for o in gedi_l2b_objs if isinstance(gedi_l2b[o], h5py.Dataset)]

        tables = dict()

        filename = gedi_l2b['METADATA']['DatasetIdentification'].attrs['fileName'].split('.h5')[0]
        timestamp = int(filename.split('_')[2])
        orbit_number = int(filename.split('_')[3][1:])
        sub_orbit_number = int(filename.split('_')[4])

        for g in tqdm(gedi_sds, desc="Processing datasets", bar_format="{desc}: {percentage:3.0f}%"):
            g_list = g.split('/')
            if len(g_list) == 2:
                key = 'base'
                inner_key = g_list[1]
            elif len(g_list) == 3:
                key = g_list[1]
                inner_key = g_list[2]
            else:
                continue

            if len(gedi_l2b[g].shape) == 2:
                all_data = gedi_l2b[g][()]
                for i in range(gedi_l2b[g].shape[1]):
                    values = []
                    for a in all_data:
                        values.append(a[i])
                    cls._add_or_update_nested_item(tables, key, f"{inner_key}_{i}", values)
            else:
                if inner_key == 'pgap_theta_z':
                    for i, arr in enumerate(gedi_l2b[g][()]):
                        arr = np.array([arr])
                        for j, val in enumerate(arr.flatten()):
                            pgap_theta_z_data.append({
                                'shot_number': i,
                                'array_index': j,
                                'value': val
                            })
                    continue
                values = list(gedi_l2b[g][()])
                cls._add_or_update_nested_item(tables, key, inner_key, values)

        with tqdm(total=6, desc="Creating DataFrames", bar_format="{desc}: {percentage:3.0f}%") as pbar:
            base = pd.DataFrame(tables.get('base'))
            pbar.update(1)

            n_rows = len(base)
            base['orbit_number'] = [orbit_number] * n_rows
            base['sub_orbit_number'] = [sub_orbit_number] * n_rows
            pbar.update(1)

            geolocation = pd.DataFrame(tables.get('geolocation'))
            pbar.update(1)

            rx_processing = pd.DataFrame(tables.get('rx_processing'))
            pbar.update(1)

            land_cover = pd.DataFrame(tables.get('land_cover_data'))
            land_cover['shot_number'] = base['shot_number']
            pbar.update(1)

            ancillary = pd.DataFrame(tables.get('ancillary'))
            ancillary['orbit_number'] = orbit_number
            ancillary['sub_orbit_number'] = sub_orbit_number
            pbar.update(1)

            pgap_theta_z_df = pd.DataFrame(pgap_theta_z_data)
            pbar.update(1)

        return L2B(base, land_cover, rx_processing, ancillary, pgap_theta_z_df, geolocation)

    @classmethod
    def hd5_list_to_l2b(cls, hd5_files, clip_gdf=None):
        """
        Converts a list of HDF5 files to a single, merged L2B object.

        Args:
            hd5_files (list of str): The list of HDF5 file paths.
            clip_gdf (GeoDataFrame, optional): The GeoDataFrame to clip the data by.

        Returns:
            L2B: A merged L2B object containing the converted data from all the input HDF5 files.

        Raises:
            Warning: If no clipping shape is provided, a warning about high memory usage is raised.

        Example:
            >>> l2b_data = GediTransformer.hd5_list_to_l2b(["path1.hd5", "path2.hd5"], clip_gdf=some_shape)
            >>> print(type(l2b_data))
            <class 'gedi_tools.classes.l2b.L2B'>
        """
        if clip_gdf is None:
            warnings.warn("No clipping shape provided. This may result in high memory usage.")
        master_l2b = None
        for hd5_file in hd5_files:
            l2b = cls.hd5_to_l2b(hd5_file)
            if clip_gdf is not None:
                l2b.clip(clip_gdf)
            if master_l2b is None:
                master_l2b = l2b
            else:
                master_l2b.merge(l2b)
        return master_l2b
