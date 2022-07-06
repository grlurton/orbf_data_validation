#%%
import pandas as pd
from blsqpy.postgres_hook import PostgresHook
from blsqpy.dhis2 import Dhis2
import matplotlib.pyplot as plt

pgHook = PostgresHook('local_pdss')
dhis = Dhis2(pgHook)
dhis.build_de_cc_table()

de_maps_id = pd.read_excel("credes_monitoring/data/raw/mapping_sheet.xlsx", 1)
de_maps_name = pd.read_excel("credes_monitoring/data/raw/mapping_sheet.xlsx", 0)

declared_data_raw = dhis.get_data(de_maps_id.dec.to_list())
validated_data_raw = dhis.get_data(de_maps_id.val.to_list())

#%%
def keep_only_relevand(df, name_serie, id_serie):
    df = df.drop(["created", "quarterly"], 1)
    df = df.rename(columns={"value":name_serie,
                            "dataelementid":id_serie,
                            "dataelementname":"name_"+name_serie})
    df = df.merge(de_maps_id)
    return df


declared_data = keep_only_relevand(declared_data_raw, "declared", "dec")
validated_data = keep_only_relevand(validated_data_raw, "validated", "val")

#%%
consolidated_data = declared_data.merge(validated_data)
consolidated_data.to_csv("data/raw/pdss_consolidated.csv")
