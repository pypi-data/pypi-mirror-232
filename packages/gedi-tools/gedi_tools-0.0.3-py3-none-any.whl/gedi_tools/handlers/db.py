#
#
# class DatabaseDroid:
#     def __init__(self, database_url):
#         self.database_url = database_url
#
#     def create_gedi2b_tables(self, base_table_name, geolocation_table_name, ancillary_table_name, land_cover_table_name,
#                              rx_processing_table_name):
#         conn = psycopg2.connect(self.database_url)
#         cur = conn.cursor()
#         conn.autocommit = True
#
#         table_sql = sql.SQL(
#             """
#                 CREATE TABLE IF NOT EXISTS {ancillary_table}
#                 (
#                     dz double precision,
#                     l2a_alg_count integer,
#                     maxheight_cuttoff double precision,
#                     rg_eg_constraint_center_buffer integer,
#                     rg_eg_mpfit_max_func_evals smallint,
#                     rg_eg_mpfit_maxiters smallint,
#                     rg_eg_mpfit_tolerance double precision,
#                     signal_search_buff double precision,
#                     tx_noise_stddev_multiplier double precision,
#                     orbit_number integer NOT NULL,
#                     sub_orbit_number smallint NOT NULL,
#                     PRIMARY KEY (orbit_number, sub_orbit_number)
#                 );
#
#                CREATE TABLE IF NOT EXISTS {base_table}
#                 (
#                     algorithmrun_flag smallint,
#                     beam smallint,
#                     channel smallint,
#                     cover real,
#                     cover_z_0 real,
#                     cover_z_1 real,
#                     cover_z_2 real,
#                     cover_z_3 real,
#                     cover_z_4 real,
#                     cover_z_5 real,
#                     cover_z_6 real,
#                     cover_z_7 real,
#                     cover_z_8 real,
#                     cover_z_9 real,
#                     cover_z_10 real,
#                     cover_z_11 real,
#                     cover_z_12 real,
#                     cover_z_13 real,
#                     cover_z_14 real,
#                     cover_z_15 real,
#                     cover_z_16 real,
#                     cover_z_17 real,
#                     cover_z_18 real,
#                     cover_z_19 real,
#                     cover_z_20 real,
#                     cover_z_21 real,
#                     cover_z_22 real,
#                     cover_z_23 real,
#                     cover_z_24 real,
#                     cover_z_25 real,
#                     cover_z_26 real,
#                     cover_z_27 real,
#                     cover_z_28 real,
#                     cover_z_29 real,
#                     fhd_normal real,
#                     l2a_quality_flag smallint,
#                     l2b_quality_flag smallint,
#                     master_frac double precision,
#                     master_int bigint,
#                     num_detectedmodes smallint,
#                     omega real,
#                     pai real,
#                     pai_z_0 real,
#                     pai_z_1 real,
#                     pai_z_2 real,
#                     pai_z_3 real,
#                     pai_z_4 real,
#                     pai_z_5 real,
#                     pai_z_6 real,
#                     pai_z_7 real,
#                     pai_z_8 real,
#                     pai_z_9 real,
#                     pai_z_10 real,
#                     pai_z_11 real,
#                     pai_z_12 real,
#                     pai_z_13 real,
#                     pai_z_14 real,
#                     pai_z_15 real,
#                     pai_z_16 real,
#                     pai_z_17 real,
#                     pai_z_18 real,
#                     pai_z_19 real,
#                     pai_z_20 real,
#                     pai_z_21 real,
#                     pai_z_22 real,
#                     pai_z_23 real,
#                     pai_z_24 real,
#                     pai_z_25 real,
#                     pai_z_26 real,
#                     pai_z_27 real,
#                     pai_z_28 real,
#                     pai_z_29 real,
#                     pavd_z_0 real,
#                     pavd_z_1 real,
#                     pavd_z_2 real,
#                     pavd_z_3 real,
#                     pavd_z_4 real,
#                     pavd_z_5 real,
#                     pavd_z_6 real,
#                     pavd_z_7 real,
#                     pavd_z_8 real,
#                     pavd_z_9 real,
#                     pavd_z_10 real,
#                     pavd_z_11 real,
#                     pavd_z_12 real,
#                     pavd_z_13 real,
#                     pavd_z_14 real,
#                     pavd_z_15 real,
#                     pavd_z_16 real,
#                     pavd_z_17 real,
#                     pavd_z_18 real,
#                     pavd_z_19 real,
#                     pavd_z_20 real,
#                     pavd_z_21 real,
#                     pavd_z_22 real,
#                     pavd_z_23 real,
#                     pavd_z_24 real,
#                     pavd_z_25 real,
#                     pavd_z_26 real,
#                     pavd_z_27 real,
#                     pavd_z_28 real,
#                     pavd_z_29 real,
#                     pgap_theta real,
#                     pgap_theta_error real,
#                     rg real,
#                     rh100 integer,
#                     rhog real,
#                     rhog_error real,
#                     rhov real,
#                     rhov_error real,
#                     rossg real,
#                     rv real,
#                     rx_range_highestreturn double precision,
#                     rx_sample_count bigint,
#                     rx_sample_start_index bigint,
#                     selected_l2a_algorithm smallint,
#                     selected_mode smallint,
#                     selected_mode_flag smallint,
#                     selected_rg_algorithm smallint,
#                     sensitivity real,
#                     shot_number bigint NOT NULL,
#                     stale_return_flag smallint,
#                     surface_flag smallint,
#                     orbit_number integer NOT NULL,
#                     sub_orbit_number smallint NOT NULL,
#                     geometry geography(POINT, 4326),
#                     PRIMARY KEY(shot_number),
#                     CONSTRAINT fk_ancillary FOREIGN KEY (orbit_number, sub_orbit_number) REFERENCES {ancillary_table}(orbit_number, sub_orbit_number)
#                 );
#                CREATE INDEX IF NOT EXISTS idx_geom ON {base_table} USING gist (geometry);
#
#                CREATE TABLE IF NOT EXISTS {geolocation_table}
#                 (
#                     shot_number bigint NOT NULL,
#                     degrade_flag smallint,
#                     delta_time double precision,
#                     digital_elevation_model real,
#                     elev_highestreturn real,
#                     elev_lowestmode real,
#                     elevation_bin0 double precision,
#                     elevation_bin0_error real,
#                     elevation_lastbin double precision,
#                     elevation_lastbin_error real,
#                     height_bin0 real,
#                     height_lastbin real,
#                     geometry_highestreturn geography(POINT, 4326),
#                     geometry_lowestmode geography(POINT, 4326),
#                     geometry_bin0 geography(POINT, 4326),
#                     geometry_lastbin geography(POINT, 4326),
#                     longitude_bin0_error real,
#                     latitude_bin0_error real,
#                     longitude_lastbin_error real,
#                     latitude_lastbin_error real,
#                     local_beam_azimuth real,
#                     local_beam_elevation real,
#                     solar_azimuth real,
#                     solar_elevation real,
#                     PRIMARY KEY(shot_number),
#                     CONSTRAINT fk_base FOREIGN KEY(shot_number) REFERENCES {base_table}(shot_number)
#                 );
#                CREATE INDEX IF NOT EXISTS idx_geom_hr ON {geolocation_table} USING gist (geometry_highestreturn);
#                CREATE INDEX IF NOT EXISTS idx_geom_lm ON {geolocation_table} USING gist (geometry_lowestmode);
#                CREATE INDEX IF NOT EXISTS idx_geom_b0 ON {geolocation_table} USING gist (geometry_bin0);
#                CREATE INDEX IF NOT EXISTS idx_geom_lb ON {geolocation_table} USING gist (geometry_lastbin);
#
#                CREATE TABLE IF NOT EXISTS {land_cover_table}
#                 (
#                     landsat_treecover real,
#                     landsat_water_persistence smallint,
#                     leaf_off_doy smallint,
#                     leaf_off_flag smallint,
#                     leaf_on_cycle smallint,
#                     leaf_on_doy smallint,
#                     modis_nonvegetated real,
#                     modis_nonvegetated_sd real,
#                     modis_treecover real,
#                     modis_treecover_sd real,
#                     pft_class smallint,
#                     region_class smallint,
#                     urban_focal_window_size smallint,
#                     urban_proportion smallint,
#                     shot_number bigint NOT NULL,
#                     PRIMARY KEY (shot_number),
#                     CONSTRAINT fk_base FOREIGN KEY(shot_number) REFERENCES {base_table}(shot_number)
#                 );
#
#                 CREATE TABLE IF NOT EXISTS {rx_processing_table}
#                 (
#                     algorithmrun_flag_a1 smallint,
#                     algorithmrun_flag_a2 smallint,
#                     algorithmrun_flag_a3 smallint,
#                     algorithmrun_flag_a4 smallint,
#                     algorithmrun_flag_a5 smallint,
#                     algorithmrun_flag_a6 smallint,
#                     pgap_theta_a1 real,
#                     pgap_theta_a2 real,
#                     pgap_theta_a3 real,
#                     pgap_theta_a4 real,
#                     pgap_theta_a5 real,
#                     pgap_theta_a6 real,
#                     pgap_theta_error_a1 real,
#                     pgap_theta_error_a2 real,
#                     pgap_theta_error_a3 real,
#                     pgap_theta_error_a4 real,
#                     pgap_theta_error_a5 real,
#                     pgap_theta_error_a6 real,
#                     rg_a1 real,
#                     rg_a2 real,
#                     rg_a3 real,
#                     rg_a4 real,
#                     rg_a5 real,
#                     rg_a6 real,
#                     rg_eg_amplitude_a1 real,
#                     rg_eg_amplitude_a2 real,
#                     rg_eg_amplitude_a3 real,
#                     rg_eg_amplitude_a4 real,
#                     rg_eg_amplitude_a5 real,
#                     rg_eg_amplitude_a6 real,
#                     rg_eg_amplitude_error_a1 real,
#                     rg_eg_amplitude_error_a2 real,
#                     rg_eg_amplitude_error_a3 real,
#                     rg_eg_amplitude_error_a4 real,
#                     rg_eg_amplitude_error_a5 real,
#                     rg_eg_amplitude_error_a6 real,
#                     rg_eg_center_a1 real,
#                     rg_eg_center_a2 real,
#                     rg_eg_center_a3 real,
#                     rg_eg_center_a4 real,
#                     rg_eg_center_a5 real,
#                     rg_eg_center_a6 real,
#                     rg_eg_center_error_a1 real,
#                     rg_eg_center_error_a2 real,
#                     rg_eg_center_error_a3 real,
#                     rg_eg_center_error_a4 real,
#                     rg_eg_center_error_a5 real,
#                     rg_eg_center_error_a6 real,
#                     rg_eg_chisq_a1 real,
#                     rg_eg_chisq_a2 real,
#                     rg_eg_chisq_a3 real,
#                     rg_eg_chisq_a4 real,
#                     rg_eg_chisq_a5 real,
#                     rg_eg_chisq_a6 real,
#                     rg_eg_flag_a1 smallint,
#                     rg_eg_flag_a2 smallint,
#                     rg_eg_flag_a3 smallint,
#                     rg_eg_flag_a4 smallint,
#                     rg_eg_flag_a5 smallint,
#                     rg_eg_flag_a6 smallint,
#                     rg_eg_gamma_a1 real,
#                     rg_eg_gamma_a2 real,
#                     rg_eg_gamma_a3 real,
#                     rg_eg_gamma_a4 real,
#                     rg_eg_gamma_a5 real,
#                     rg_eg_gamma_a6 real,
#                     rg_eg_gamma_error_a1 real,
#                     rg_eg_gamma_error_a2 real,
#                     rg_eg_gamma_error_a3 real,
#                     rg_eg_gamma_error_a4 real,
#                     rg_eg_gamma_error_a5 real,
#                     rg_eg_gamma_error_a6 real,
#                     rg_eg_niter_a1 integer,
#                     rg_eg_niter_a2 integer,
#                     rg_eg_niter_a3 integer,
#                     rg_eg_niter_a4 integer,
#                     rg_eg_niter_a5 integer,
#                     rg_eg_niter_a6 integer,
#                     rg_eg_sigma_a1 real,
#                     rg_eg_sigma_a2 real,
#                     rg_eg_sigma_a3 real,
#                     rg_eg_sigma_a4 real,
#                     rg_eg_sigma_a5 real,
#                     rg_eg_sigma_a6 real,
#                     rg_eg_sigma_error_a1 real,
#                     rg_eg_sigma_error_a2 real,
#                     rg_eg_sigma_error_a3 real,
#                     rg_eg_sigma_error_a4 real,
#                     rg_eg_sigma_error_a5 real,
#                     rg_eg_sigma_error_a6 real,
#                     rg_error_a1 real,
#                     rg_error_a2 real,
#                     rg_error_a3 real,
#                     rg_error_a4 real,
#                     rg_error_a5 real,
#                     rg_error_a6 real,
#                     rv_a1 real,
#                     rv_a2 real,
#                     rv_a3 real,
#                     rv_a4 real,
#                     rv_a5 real,
#                     rv_a6 real,
#                     rx_energy_a1 real,
#                     rx_energy_a2 real,
#                     rx_energy_a3 real,
#                     rx_energy_a4 real,
#                     rx_energy_a5 real,
#                     rx_energy_a6 real,
#                     shot_number bigint NOT NULL,
#                     PRIMARY KEY (shot_number),
#                     CONSTRAINT fk_base FOREIGN KEY(shot_number) REFERENCES {base_table}(shot_number)
#                 );
#            """).format(
#             base_table=sql.Identifier(base_table_name),
#             geolocation_table=sql.Identifier(geolocation_table_name),
#             land_cover_table=sql.Identifier(land_cover_table_name),
#             ancillary_table=sql.Identifier(ancillary_table_name),
#             rx_processing_table=sql.Identifier(rx_processing_table_name)
#         )
#
#         cur.execute(table_sql)
#         cur.close()
#         conn.close()
#
#     def _gedi2b_base2psql(self, base, table_name):
#         conn = psycopg2.connect(self.database_url)
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         values = tuple([tuple(row[:-1] + [row[-1].wkt]) for row in base.to_numpy(dtype='O').tolist()])
#
#         upsert_statement = sql.SQL("""
#         INSERT INTO {table}
#          (
#             algorithmrun_flag,
#             beam,
#             channel,
#             cover,
#             cover_z_0,
#             cover_z_1,
#             cover_z_2,
#             cover_z_3,
#             cover_z_4,
#             cover_z_5,
#             cover_z_6,
#             cover_z_7,
#             cover_z_8,
#             cover_z_9,
#             cover_z_10,
#             cover_z_11,
#             cover_z_12,
#             cover_z_13,
#             cover_z_14,
#             cover_z_15,
#             cover_z_16,
#             cover_z_17,
#             cover_z_18,
#             cover_z_19,
#             cover_z_20,
#             cover_z_21,
#             cover_z_22,
#             cover_z_23,
#             cover_z_24,
#             cover_z_25,
#             cover_z_26,
#             cover_z_27,
#             cover_z_28,
#             cover_z_29,
#             fhd_normal,
#             l2a_quality_flag,
#             l2b_quality_flag,
#             master_frac,
#             master_int,
#             num_detectedmodes,
#             omega,
#             pai,
#             pai_z_0,
#             pai_z_1,
#             pai_z_2,
#             pai_z_3,
#             pai_z_4,
#             pai_z_5,
#             pai_z_6,
#             pai_z_7,
#             pai_z_8,
#             pai_z_9,
#             pai_z_10,
#             pai_z_11,
#             pai_z_12,
#             pai_z_13,
#             pai_z_14,
#             pai_z_15,
#             pai_z_16,
#             pai_z_17,
#             pai_z_18,
#             pai_z_19,
#             pai_z_20,
#             pai_z_21,
#             pai_z_22,
#             pai_z_23,
#             pai_z_24,
#             pai_z_25,
#             pai_z_26,
#             pai_z_27,
#             pai_z_28,
#             pai_z_29,
#             pavd_z_0,
#             pavd_z_1,
#             pavd_z_2,
#             pavd_z_3,
#             pavd_z_4,
#             pavd_z_5,
#             pavd_z_6,
#             pavd_z_7,
#             pavd_z_8,
#             pavd_z_9,
#             pavd_z_10,
#             pavd_z_11,
#             pavd_z_12,
#             pavd_z_13,
#             pavd_z_14,
#             pavd_z_15,
#             pavd_z_16,
#             pavd_z_17,
#             pavd_z_18,
#             pavd_z_19,
#             pavd_z_20,
#             pavd_z_21,
#             pavd_z_22,
#             pavd_z_23,
#             pavd_z_24,
#             pavd_z_25,
#             pavd_z_26,
#             pavd_z_27,
#             pavd_z_28,
#             pavd_z_29,
#             pgap_theta,
#             pgap_theta_error,
#             rg,
#             rh100,
#             rhog,
#             rhog_error,
#             rhov,
#             rhov_error,
#             rossg,
#             rv,
#             rx_range_highestreturn,
#             rx_sample_count,
#             rx_sample_start_index,
#             selected_l2a_algorithm,
#             selected_mode,
#             selected_mode_flag,
#             selected_rg_algorithm,
#             sensitivity,
#             shot_number,
#             stale_return_flag,
#             surface_flag,
#             orbit_number,
#             sub_orbit_number,
#             geometry
#          )
#          VALUES %s
#          ON CONFLICT ("shot_number") DO NOTHING
#         """).format(table=sql.Identifier(table_name))
#
#         foo = execute_values(
#             cur,
#             upsert_statement,
#             values,
#             template="""
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     ST_GeomFromText(%s, 4326)
#                 )
#             """,
#             page_size=200
#         )
#         cur.close()
#         conn.close()
#         return foo
#
#     def _gedi2b_geolocation2psql(self, geolocation, table_name):
#         conn = psycopg2.connect(self.database_url)
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         values = tuple([
#             (
#                 row[25],
#                 row[0],
#                 row[1],
#                 row[2],
#                 row[3],
#                 row[4],
#                 row[5],
#                 row[6],
#                 row[7],
#                 row[8],
#                 row[9],
#                 row[10],  # height_lastbin
#                 row[19],  # lon_highestreturn
#                 row[11],  # lat_highestreturn
#                 row[20],  # lon_lowestmode
#                 row[12],  # lat_lowestmode
#                 row[21],  # longitude_bin0
#                 row[13],  # latitude_bin0
#                 row[23],  # longitude_lastbin
#                 row[15],  # latitude_lastbin
#                 row[22],  # longitude_bin0_error
#                 row[14],  # latitude_bin0_error
#                 row[24],  # longitude_lastbin_error
#                 row[16],  # latitude_lastbin_error
#                 row[17],  # local_beam_azimuth
#                 row[18],  # local_beam_elevation
#                 row[26],  # solar_azimuth
#                 row[27]  # solar_elevation
#             ) for row in geolocation.to_numpy(dtype='O').tolist()])
#
#         upsert_statement = sql.SQL("""
#         INSERT INTO {table}
#          (
#                 shot_number,
#                 degrade_flag,
#                 delta_time,
#                 digital_elevation_model,
#                 elev_highestreturn,
#                 elev_lowestmode,
#                 elevation_bin0,
#                 elevation_bin0_error,
#                 elevation_lastbin,
#                 elevation_lastbin_error,
#                 height_bin0,
#                 height_lastbin,
#                 geometry_highestreturn,
#                 geometry_lowestmode,
#                 geometry_bin0,
#                 geometry_lastbin,
#                 longitude_bin0_error,
#                 latitude_bin0_error,
#                 longitude_lastbin_error,
#                 latitude_lastbin_error,
#                 local_beam_azimuth,
#                 local_beam_elevation,
#                 solar_azimuth,
#                 solar_elevation
#          )
#          VALUES %s
#          ON CONFLICT ("shot_number") DO NOTHING
#         """).format(table=sql.Identifier(table_name))
#
#         execute_values(
#             cur,
#             upsert_statement,
#             values,
#             template="""
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     ST_GeomFromText('POINT(%s %s)', 4326),
#                     ST_GeomFromText('POINT(%s %s)', 4326),
#                     ST_GeomFromText('POINT(%s %s)', 4326),
#                     ST_GeomFromText('POINT(%s %s)', 4326),
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s
#                 )
#             """,
#         )
#         cur.close()
#         conn.close()
#
#     def _gedi2b_landcover2psql(self, landcover, table_name):
#         conn = psycopg2.connect(self.database_url)
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         values = tuple(landcover.to_numpy(dtype='O').tolist())
#
#         upsert_statement = sql.SQL("""
#         INSERT INTO {table}
#          (
#                 landsat_treecover,
#                 landsat_water_persistence,
#                 leaf_off_doy,
#                 leaf_off_flag,
#                 leaf_on_cycle,
#                 leaf_on_doy,
#                 modis_nonvegetated,
#                 modis_nonvegetated_sd,
#                 modis_treecover,
#                 modis_treecover_sd,
#                 pft_class,
#                 region_class,
#                 urban_focal_window_size,
#                 urban_proportion,
#                 shot_number
#          )
#          VALUES %s
#          ON CONFLICT ("shot_number") DO NOTHING
#         """).format(table=sql.Identifier(table_name))
#
#         execute_values(
#             cur,
#             upsert_statement,
#             values,
#             template="""
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s
#                 )
#             """,
#         )
#         cur.close()
#         conn.close()
#
#     def _gedi2b_ancillary2psql(self, ancillary, table_name):
#         conn = psycopg2.connect(self.database_url)
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         values = tuple(ancillary.to_numpy(dtype='O').tolist())
#
#         upsert_statement = sql.SQL("""
#         INSERT INTO {table}
#          (
#             dz,
#             l2a_alg_count,
#             maxheight_cuttoff,
#             rg_eg_constraint_center_buffer,
#             rg_eg_mpfit_max_func_evals,
#             rg_eg_mpfit_maxiters,
#             rg_eg_mpfit_tolerance,
#             signal_search_buff,
#             tx_noise_stddev_multiplier,
#             orbit_number,
#             sub_orbit_number
#          )
#          VALUES %s
#          ON CONFLICT ("orbit_number", "sub_orbit_number") DO NOTHING
#         """).format(table=sql.Identifier(table_name))
#
#         execute_values(
#             cur,
#             upsert_statement,
#             values,
#             template="""
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s
#                 )
#             """,
#         )
#         cur.close()
#         conn.close()
#
#     def _gedi2b_rx_processing2psql(self, rx_processing, table_name):
#         conn = psycopg2.connect(self.database_url)
#         conn.autocommit = True
#         cur = conn.cursor()
#
#         values = tuple(rx_processing.to_numpy(dtype='O').tolist())
#
#         upsert_statement = sql.SQL("""
#         INSERT INTO {table}
#          (
#             algorithmrun_flag_a1,
#                 algorithmrun_flag_a2,
#                 algorithmrun_flag_a3,
#                 algorithmrun_flag_a4,
#                 algorithmrun_flag_a5,
#                 algorithmrun_flag_a6,
#                 pgap_theta_a1,
#                 pgap_theta_a2,
#                 pgap_theta_a3,
#                 pgap_theta_a4,
#                 pgap_theta_a5,
#                 pgap_theta_a6,
#                 pgap_theta_error_a1,
#                 pgap_theta_error_a2,
#                 pgap_theta_error_a3,
#                 pgap_theta_error_a4,
#                 pgap_theta_error_a5,
#                 pgap_theta_error_a6,
#                 rg_a1,
#                 rg_a2,
#                 rg_a3,
#                 rg_a4,
#                 rg_a5,
#                 rg_a6,
#                 rg_eg_amplitude_a1,
#                 rg_eg_amplitude_a2,
#                 rg_eg_amplitude_a3,
#                 rg_eg_amplitude_a4,
#                 rg_eg_amplitude_a5,
#                 rg_eg_amplitude_a6,
#                 rg_eg_amplitude_error_a1,
#                 rg_eg_amplitude_error_a2,
#                 rg_eg_amplitude_error_a3,
#                 rg_eg_amplitude_error_a4,
#                 rg_eg_amplitude_error_a5,
#                 rg_eg_amplitude_error_a6,
#                 rg_eg_center_a1,
#                 rg_eg_center_a2,
#                 rg_eg_center_a3,
#                 rg_eg_center_a4,
#                 rg_eg_center_a5,
#                 rg_eg_center_a6,
#                 rg_eg_center_error_a1,
#                 rg_eg_center_error_a2,
#                 rg_eg_center_error_a3,
#                 rg_eg_center_error_a4,
#                 rg_eg_center_error_a5,
#                 rg_eg_center_error_a6,
#                 rg_eg_chisq_a1,
#                 rg_eg_chisq_a2,
#                 rg_eg_chisq_a3,
#                 rg_eg_chisq_a4,
#                 rg_eg_chisq_a5,
#                 rg_eg_chisq_a6,
#                 rg_eg_flag_a1,
#                 rg_eg_flag_a2,
#                 rg_eg_flag_a3,
#                 rg_eg_flag_a4,
#                 rg_eg_flag_a5,
#                 rg_eg_flag_a6,
#                 rg_eg_gamma_a1,
#                 rg_eg_gamma_a2,
#                 rg_eg_gamma_a3,
#                 rg_eg_gamma_a4,
#                 rg_eg_gamma_a5,
#                 rg_eg_gamma_a6,
#                 rg_eg_gamma_error_a1,
#                 rg_eg_gamma_error_a2,
#                 rg_eg_gamma_error_a3,
#                 rg_eg_gamma_error_a4,
#                 rg_eg_gamma_error_a5,
#                 rg_eg_gamma_error_a6,
#                 rg_eg_niter_a1,
#                 rg_eg_niter_a2,
#                 rg_eg_niter_a3,
#                 rg_eg_niter_a4,
#                 rg_eg_niter_a5,
#                 rg_eg_niter_a6,
#                 rg_eg_sigma_a1,
#                 rg_eg_sigma_a2,
#                 rg_eg_sigma_a3,
#                 rg_eg_sigma_a4,
#                 rg_eg_sigma_a5,
#                 rg_eg_sigma_a6,
#                 rg_eg_sigma_error_a1,
#                 rg_eg_sigma_error_a2,
#                 rg_eg_sigma_error_a3,
#                 rg_eg_sigma_error_a4,
#                 rg_eg_sigma_error_a5,
#                 rg_eg_sigma_error_a6,
#                 rg_error_a1,
#                 rg_error_a2,
#                 rg_error_a3,
#                 rg_error_a4,
#                 rg_error_a5,
#                 rg_error_a6,
#                 rv_a1,
#                 rv_a2,
#                 rv_a3,
#                 rv_a4,
#                 rv_a5,
#                 rv_a6,
#                 rx_energy_a1,
#                 rx_energy_a2,
#                 rx_energy_a3,
#                 rx_energy_a4,
#                 rx_energy_a5,
#                 rx_energy_a6,
#                 shot_number
#          )
#          VALUES %s
#          ON CONFLICT ("shot_number") DO NOTHING
#         """).format(table=sql.Identifier(table_name))
#
#         execute_values(
#             cur,
#             upsert_statement,
#             values,
#             template="""
#                 (
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s,
#                     %s
#                 )
#             """,
#         )
#         cur.close()
#         conn.close()
#
#     def l2b_2_postgis(self, path, base_table_name, geolocation_table_name, ancillary_table_name, land_cover_table_name,
#                       rx_processing_table_name, clean=True):
#         """
#         Imports GEDI Level 2B data into a PostGIS enabled PostgreSQL database.
#
#         :param path: str
#             Path to the directory containing the GEDI L2B files to import to the database.
#         :param base_table_name: str
#             The name of the table to import the "base" data into. See notes below for details.
#         :param geolocation_table_name: str
#             The name of the table to import the "geolocation" data into. See notes below for details.
#         :param ancillary_table_name: str
#             The name of the table to import the "ancillary" data into. See notes below for details.
#         :param land_cover_table_name: str
#             The name of the table to import the "land cover" data into. See notes below for details.
#         :param rx_processing_table_name: str
#             The name of the table to import the "rx processing" data into. See notes below for details.
#         :param clean: bool
#             If True, perform simple quality filtering. Only footprints with a L2A Quality Flag of 1, a
#             L2B Quality Flag of 1, a Degrade Flag less than 1, and a region class that is not 0 (ocean) will be kept.
#         :return: None
#
#         Notes
#         -----
#         WIP
#         """
#
#         self.create_gedi2b_tables(base_table_name, geolocation_table_name, ancillary_table_name, land_cover_table_name,
#                                   rx_processing_table_name)
#
#         files = list_h5_files(path)
#         for h5_file in files:
#             base, geolocation, land_cover, rx_processing, ancillary = read_l2b_hd5_file(h5_file, clean=clean)
#             self._gedi2b_ancillary2psql(ancillary, ancillary_table_name)
#             self._gedi2b_base2psql(base, base_table_name)
#             self._gedi2b_geolocation2psql(geolocation, geolocation_table_name)
#             self._gedi2b_landcover2psql(land_cover, land_cover_table_name)
#             self._gedi2b_rx_processing2psql(rx_processing, rx_processing_table_name)
