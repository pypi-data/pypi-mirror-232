
# ### these both syntax works fine
#from omshakya._sharedcode import _sqloperations as __sqlo
from .. _bin_cc_or_sc import _jsonops as __jsono

from .. _bin_cc_or_sc import __version__ as __v
__version__ = __v.__VERSION__

"""
Utility functions related to json.
"""

def write_df_to_jsonfile(df, jsonfilename, tracing = False):
    """
    Write the pandas dataframe into a .json file.
    
    Parameters:
        df (pandas dataframe): pandas dataframe
        jsonfilename (str): the name/path of the json file to write
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        True/False: 'True' if dataframe written to json file else 'False'
    """
    return __jsono.JsonOpsWrapper.write_df_to_json(df, jsonfilename, tracing)

def read_jsonfile(jsonfilename, tracing = False):
    """
    Read the .json file.
    
    Parameters:
        jsonfilename (str): the name/path of the json file to read
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        json data: The json data of the file
    """
    return __jsono.JsonOpsWrapper.read_json(jsonfilename, tracing)
