#%%
import itertools
import os
import pandas as pd
#import csv
import olefile
#%%
def combine_paths(directory, files):
    return (os.path.join(directory, filename) for filename in files)

def get_excel_for_district(district_path):
    files = os.walk(district_path)
    files_per_directory = [combine_paths(walk[0],walk[2]) for walk in files]
    all_files = list(itertools.chain(*files_per_directory))
    return (f for f in all_files if f.endswith('xls') or f.endswith('xlsx'))

def get_districts(root_path):
    """
    Start from the directory containing all the districts. A district is assumed to be any
    directory in root_path.
    """
    return (os.path.join(root_path,directory) for directory in os.listdir(root_path) if os.path.isdir(os.path.join(root_path,directory)))

def get_districts_with_files(root_path):
    return ((district, get_excel_for_district(district)) for district in get_districts(root_path))

def get_OLE_metadata(filename):
    print(filename)
    try :
        ole = olefile.OleFileIO(filename)
        meta = ole.get_metadata()
        metadata = {"filename": [(filename.replace("\\", "/"))],
                    "author": [meta.author],
                    "last_saved_by":[meta.last_saved_by],
                    "create_time": [meta.create_time],
                    "last_saved_time": [meta.last_saved_time]}
    except :
        metadata = {"filename":[filename.replace("\\", "/")], 
                    "problem": ["Not working"]}
    return pd.DataFrame.from_dict(metadata)

def full_function(root_path) :
    for district, files in get_districts_with_files(root_path) :
        for filename in files :
            yield get_OLE_metadata(filename)
#%%
data_path = 'data/raw/rbv_credes/'

out = pd.DataFrame()
for results in full_function(data_path) :
    out = out.append(results)
out.to_csv(data_path + "windows_metadata.csv")