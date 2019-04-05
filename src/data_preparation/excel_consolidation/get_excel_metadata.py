#%%
import xlrd
import itertools
import os
import pandas as pd

def combine_paths(directory, files):
    return (os.path.join(directory, filename) for filename in files)

def get_excel_for_district(district_path):
    files = os.walk(district_path)
    files_per_directory = [combine_paths(walk[0],walk[2]) for walk in files]
    all_files = list(itertools.chain(*files_per_directory))
    return (f for f in all_files if f.endswith(('xlsx',"xls")))

def get_districts(root_path):
    """
    Start from the directory containing all the districts. A district is assumed to be any
    directory in root_path.
    """
    return (os.path.join(root_path,directory) for directory in os.listdir(root_path) if os.path.isdir(os.path.join(root_path,directory)))

def get_districts_with_files(root_path):
    return ((district, get_excel_for_district(district)) for district in get_districts(root_path))

def get_excel_metadata(filename):
    try :
        book = xlrd.open_workbook(filename , on_demand = True )
    except :
        return ((filename.replace("\\", "/")) , "error opening file" )
    print(filename)
    try :
        if filename.endswith("xlsx"):
            metadata = {"filename":[filename.replace("\\", "/")], 
                        "user_name":[book.props["creator"]]  , 
                        "last_modif_by":[book.props["last_modified_by"]] , 
                        "created":[book.props["created"]] ,  
                        "modified":[book.props["modified"]]}
        elif filename.endswith("xls"):
            metadata = {"filename":[filename.replace("\\", "/")], 
                        "user_name":[book.user_name]}
    except :
        metadata = ((filename.replace("\\", "/")) , "file has no props")
    return pd.DataFrame.from_dict(metadata)

def full_function(root_path) :
    for district, files in get_districts_with_files(root_path) :
        for filename in files :
            yield get_excel_metadata(filename)

#%%
data_path = 'data/raw/rbv_credes/'

out = pd.DataFrame()
for results in full_function(data_path) :
    out = out.append(results)
out.to_csv(data_path + "excel_metadata.csv")
