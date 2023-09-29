import warnings
warnings.filterwarnings('ignore')
import pandas as pd

class TracerPrinterWrapper:
    '''prints any object which you want in between execution as tracing.'''

    def print(toprint, display):
        if display:
            isdf = isinstance(toprint, pd.DataFrame)
            if isdf:
                print('oms traces, df:')
                print(toprint)  
            else:
                print(f'oms traces, {toprint}')  
