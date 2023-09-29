import warnings
warnings.filterwarnings('ignore')
from . _traceprinter import TracerPrinterWrapper as trace
import json

class JsonOpsWrapper:
    '''This class interacts with mongodb and performs mongodb operations.'''
        
    '''This class interacts with sql and performs sql operations.'''

    def write_df_to_json(df, jsonfilename, tracing = False):
        try:
            trace.print(f'''write df to json: 
                        \t, jsonfilename: {jsonfilename}''', tracing)
            
            b = False
            tojson = df.to_json(orient = 'records', date_format = 'iso')
            list_json = json.loads(tojson)

            with open(jsonfilename, "w") as outfile: #"logs\custom_logs.json"
                json.dump(list_json, outfile)
                trace.print(f'write df to json executed,', tracing)
                b = True
        except Exception as ex:
            trace.print(f'write df to json failed,', tracing)
            raise Exception(ex)
        return b

    def read_json(jsonfilename, tracing = False):
        try:
            trace.print(f'''read json file: 
                        \t, jsonfilename: {jsonfilename}''', tracing)
            
            with open(jsonfilename) as json_file:
                data = json.load(json_file)
                json_data = data
                trace.print(f'read json file executed,', tracing)
            return json_data
        except Exception as ex:
            trace.print(f'read json file failed,', tracing)
            raise Exception(ex)