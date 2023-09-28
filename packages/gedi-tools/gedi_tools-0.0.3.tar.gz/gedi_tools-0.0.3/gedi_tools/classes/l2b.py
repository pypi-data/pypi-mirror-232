import pandas as pd
import geopandas as gp
import logging

from geopandas.tools import clip

logger = logging.getLogger(__name__)


class L2B:
    """
    A class to manage L2B datasets for geospatial analysis.

    Attributes:
        l2b (DataFrame): The L2B dataset.
        land_cover (DataFrame): The land cover dataset.
        rx_processing (DataFrame): The RX processing dataset.
        ancillary (DataFrame): The ancillary dataset.
        pgap_theta_z (DataFrame): The PGAP theta Z dataset.
        geolocation (DataFrame): The geolocation dataset.

    Examples:
        >>> l2b_obj = L2B(l2b, land_cover, rx_processing, ancillary, pgap_theta_z, geolocation)
        >>> l2b_obj.clean()
        >>> l2b_obj.add_acquisition_time()
    """
    GEOMETRY_COLUMN_X = 'lon_lowestmode'
    GEOMETRY_COLUMN_Y = 'lat_lowestmode'
    CRS = 'EPSG:4326'
    SENSITIVITY_THRESHOLD = 0.95
    BASE_TIME = '2018-01-01'

    def __init__(self, l2b, land_cover, rx_processing, ancillary, pgap_theta_z, geolocation):
        """
        Initializes the L2B object with multiple datasets.

        Args:
            l2b (DataFrame): The L2B dataset.
            land_cover (DataFrame): The land cover dataset.
            rx_processing (DataFrame): The RX processing dataset.
            ancillary (DataFrame): The ancillary dataset.
            pgap_theta_z (DataFrame): The PGAP theta Z dataset.
            geolocation (DataFrame): The geolocation dataset.
        """
        self.l2b = l2b
        self.land_cover = land_cover
        self.rx_processing = rx_processing
        self.ancillary = ancillary
        self.pgap_theta_z = pgap_theta_z
        self.geolocation = geolocation

    def add_acquisition_time(self):
        """Adds an 'acquisition_time' column to the L2B DataFrame."""
        base_datetime = pd.Timestamp(self.BASE_TIME)
        delta_time_series = pd.to_timedelta(self.geolocation['delta_time'], unit='s')
        self.l2b['acquisition_time'] = base_datetime + delta_time_series

    def clean(self, inplace=True):
        """
        Cleans the datasets by applying quality flags and other conditions.

        Args:
            inplace (bool, optional): Whether to perform the cleaning inplace. Defaults to True.

        Returns:
            L2B: If inplace is False, returns a new instance of L2B with cleaned data.
        """
        df = pd.merge(
            self.l2b[["shot_number", "l2a_quality_flag", "l2b_quality_flag", "sensitivity"]],
            self.geolocation[["shot_number", "degrade_flag"]],
            on=["shot_number"]
        ).merge(
            self.land_cover[["shot_number", "region_class"]], on='shot_number'
        )
        df = df.loc[
            (df['l2a_quality_flag'] == 1) &
            (df['l2b_quality_flag'] == 1) &
            (df['degrade_flag'] < 1) &
            (df['region_class'] != 0) &
            (df['sensitivity'] >= self.SENSITIVITY_THRESHOLD)
            ]

        shot_numbers_to_keep = df['shot_number'].unique()

        if inplace:
            self._update_dfs(shot_numbers_to_keep)
        else:
            new_obj = self.__class__(self.l2b.copy(), self.land_cover.copy(),
                                     self.rx_processing.copy(), self.ancillary.copy(),
                                     self.pgap_theta_z.copy(), self.geolocation.copy())
            new_obj._update_dfs(shot_numbers_to_keep)
            return new_obj

    def _create_geometry(self, df):
        """
        Creates geometry for GeoDataFrame.

        Args:
            df (DataFrame): DataFrame containing the columns specified in GEOMETRY_COLUMN_X and GEOMETRY_COLUMN_Y.

        Returns:
            GeoDataFrame: A new GeoDataFrame with geometry.

        Raises:
            KeyError: If GEOMETRY_COLUMN_X or GEOMETRY_COLUMN_Y is not in DataFrame.
        """
        if self.GEOMETRY_COLUMN_X not in df.columns or self.GEOMETRY_COLUMN_Y not in df.columns:
            raise KeyError(f"Columns {self.GEOMETRY_COLUMN_X} or {self.GEOMETRY_COLUMN_Y} are missing.")

        geometry = gp.points_from_xy(df[self.GEOMETRY_COLUMN_X], df[self.GEOMETRY_COLUMN_Y])
        return gp.GeoDataFrame(df, geometry=geometry, crs=self.CRS)

    def clip(self, shape, inplace=True):
        """
        Clips the geolocation dataset with a given shape.

        Args:
            shape (GeoDataFrame|GeoSeries): The shape to clip with.
            inplace (bool, optional): Whether to perform the clip inplace. Defaults to True.

        Returns:
            L2B: If inplace is False, returns a new instance of L2B with clipped data.

        Raises:
            TypeError: If shape is not a GeoDataFrame or GeoSeries.
        """
        if not isinstance(shape, (gp.GeoDataFrame, gp.GeoSeries)):
            raise TypeError("Shape should be a GeoDataFrame or GeoSeries.")

        geolocation_gdf = self._create_geometry(self.geolocation)

        clipped_geolocation = clip(geolocation_gdf, shape)

        shot_numbers_to_keep = clipped_geolocation['shot_number'].unique()

        if inplace:
            self._update_dfs(shot_numbers_to_keep, clipped_geolocation)
        else:
            new_obj = self.__class__(self.l2b.copy(), self.land_cover.copy(),
                                     self.rx_processing.copy(), self.ancillary.copy(),
                                     self.pgap_theta_z.copy(), clipped_geolocation)
            new_obj._update_dfs(shot_numbers_to_keep, clipped_geolocation)
            return new_obj

    def _update_dfs(self, shot_numbers_to_keep, clipped_geolocation=None):
        """
        Updates the DataFrames by keeping only rows with specific shot numbers.

        Args:
            shot_numbers_to_keep (array-like): Array of shot numbers to keep.
            clipped_geolocation (GeoDataFrame, optional): Optionally provide a clipped geolocation dataset.
        """
        dfs_to_update = ['l2b', 'land_cover', 'rx_processing', 'ancillary', 'pgap_theta_z']

        for df_name in dfs_to_update:
            df = self.__dict__[df_name]
            if 'shot_number' in df.columns:
                self.__dict__[df_name] = df[df['shot_number'].isin(shot_numbers_to_keep)]

        if clipped_geolocation is not None:
            self.geolocation = clipped_geolocation

    def merge(self, other, inplace=True):
        """
        Merges another L2B object with this one.

        Args:
            other (L2B): The other L2B object to merge.
            inplace (bool, optional): Whether to perform the merge inplace. Defaults to True.

        Returns:
            L2B: If inplace is False, returns a new merged instance of L2B.

        Raises:
            TypeError: If other is not an instance of L2B.
            ValueError: If DataFrame columns don't match.
        """
        if not isinstance(other, L2B):
            raise TypeError("The object to merge must be an instance of L2B.")

        for df_name in ['l2b', 'land_cover', 'rx_processing', 'ancillary', 'pgap_theta_z', 'geolocation']:
            if not self._compare_df_columns(self.__dict__[df_name], other.__dict__[df_name]):
                raise ValueError(f"Columns do not match in {df_name}.")

        if inplace:
            self._merge_dfs(other)
        else:
            new_obj = self.__class__(self.l2b.copy(), self.land_cover.copy(),
                                     self.rx_processing.copy(), self.ancillary.copy(),
                                     self.pgap_theta_z.copy(), self.geolocation.copy())
            new_obj._merge_dfs(other)
            return new_obj

    def _merge_dfs(self, other):
        """
        Performs the actual DataFrame merging operation.

        Args:
            other (L2B): The other L2B object to merge.
        """
        for df_name in ['l2b', 'land_cover', 'rx_processing', 'ancillary', 'pgap_theta_z']:
            self.__dict__[df_name] = pd.concat([self.__dict__[df_name], other.__dict__[df_name]], ignore_index=True)

        self.geolocation = gp.GeoDataFrame(pd.concat([self.geolocation, other.geolocation], ignore_index=True))

    @staticmethod
    def _compare_df_columns(df1, df2):
        """
        Compares the columns of two DataFrames.

        Args:
            df1 (DataFrame): The first DataFrame.
            df2 (DataFrame): The second DataFrame.

        Returns:
            bool: True if columns match, False otherwise.
        """
        return set(df1.columns) == set(df2.columns)

    def perform_geospatial_operation(self, operation, *args, **kwargs):
        """
        Performs a geospatial operation on the geolocation dataset.

        Args:
            operation (callable): The geospatial operation to perform.
            *args: Positional arguments for the geospatial operation.
            **kwargs: Keyword arguments for the geospatial operation.

        Returns:
            Any: Result of the geospatial operation.
        """
        geolocation_gdf = self._create_geometry(self.geolocation)
        result = operation(geolocation_gdf, *args, **kwargs)
        return result

    def export_vector_data(self, file_path, columns_to_export, driver="GPKG"):
        """
        Exports vector data to a file.

        Args:
            file_path (str): The file path to export the data.
            columns_to_export (list): List of columns to export.
            driver (str, optional): The file format. Defaults to "GPKG".
        """
        final_df = pd.DataFrame()

        missing_x = self.GEOMETRY_COLUMN_X not in columns_to_export
        missing_y = self.GEOMETRY_COLUMN_Y not in columns_to_export

        df_map = {
            'l2b': self.l2b,
            'land_cover': self.land_cover,
            'rx_processing': self.rx_processing,
            'geolocation': self.geolocation
        }

        for col in columns_to_export:
            for df_name, df in df_map.items():
                if col in df.columns:
                    final_df[col] = df[col]
                    break
            else:
                logging.warning(f"Column '{col}' does not exist in any DataFrame.")

        merge_cols = ['shot_number']
        if missing_x:
            merge_cols.append(self.GEOMETRY_COLUMN_X)
        if missing_y:
            merge_cols.append(self.GEOMETRY_COLUMN_Y)

        if len(merge_cols) > 1:
            final_df = pd.merge(
                final_df,
                self.geolocation[merge_cols],
                on='shot_number',
                how='left'
            )

        geometry = gp.points_from_xy(final_df[self.GEOMETRY_COLUMN_X], final_df[self.GEOMETRY_COLUMN_Y])
        final_gdf = gp.GeoDataFrame(final_df, geometry=geometry)
        if missing_x:
            final_gdf.drop(columns=[self.GEOMETRY_COLUMN_X], inplace=True)
        if missing_y:
            final_gdf.drop(columns=[self.GEOMETRY_COLUMN_Y], inplace=True)

        final_gdf.to_file(file_path, driver=driver)
