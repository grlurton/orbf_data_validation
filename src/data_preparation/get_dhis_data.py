import pandas as pd
from blsqpy.postgres_hook import PostgresHook
from blsqpy.dhis2 import Dhis2

pgHook = PostgresHook('local_pdss')
dhis = Dhis2(pgHook)
dhis.build_de_cc_table()

dhis.get_data

de_maps_id = pd.read_excel("credes_monitoring/data/raw/mapping_sheet.xlsx", 1)
de_maps_name = pd.read_excel("credes_monitoring/data/raw/mapping_sheet.xlsx", 0)

declared_data = dhis.get_data(de_maps_id.dec.to_list())
validated_data = dhis.get_data(de_maps_id.val.to_list())

declared_data.to_csv("data/raw/pdss_declared.csv")
validated_data.to_csv("data/raw/pdss_validated.csv")