import pandas as pd
import sqlalchemy as sa
from sqlalchemy.sql import text
import warnings
warnings.filterwarnings('ignore')
from . _traceprinter import TracerPrinterWrapper as trace


class SqlOpsWrapper:
    '''This class interacts with sql and performs sql operations.'''
    def __init__(self, cs_odbc_url):
        conn_url = sa.engine.URL.create("mssql+pyodbc", query = dict(odbc_connect = cs_odbc_url))
        engine = sa.create_engine(conn_url, fast_executemany = True)
        self.__engine = engine
    
    def __del__(self):
        #print("being automatically destroyed,")
        pass

    def check_connection(self, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        """
        trace.print(f'check sql connection,', tracing)
        status = 'sql connection failed.'
        try:
            q = 'SELECT TOP 1 object_id FROM sys.tables;'
            _ = self.select_by_script(q, tracing)
            status = 'sql connection succeeded.'
            trace.print(f'check sql connection executed,', tracing)
        except Exception as ex:
            status = 'sql connection failed.'
            trace.print(f'check sql connectionfailed,', tracing)
            raise Exception(ex)
        return status

    def select_by_script(self, query, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        """
        try:
            trace.print(f'''select by script, ''', tracing)
            trace.print(text(query), tracing)

            with self.__engine.connect() as connection:
                df = pd.read_sql_query(text(query), connection)

            trace.print(f'select by script executed successfully,', tracing)
            return df
        except Exception as ex:
            trace.print(f'select by script failed,', tracing)
            raise Exception(ex)
    
    def execute_updatescript(self, script, tracing = False):
        """It executes the sql script provided.
        
        Parameters:
            script (str): sql script
            is_result (boolean): do you need the scalar result of connection.execute(script)?

        Returns: 
            counts (scalar or number of records) : bydeafault counts = 0 which means script executed succesfully
            , counts = -1 which means some exception occured
            , otherwise  scalar result
        """
        counts = 0
        trace.print(f'''execute update script, ''', tracing)
        trace.print(text(script), tracing)
        try:
            with self.__engine.connect().execution_options(autocommit = True) as connection:
                results = connection.execute(text(script))
                
                try:
                    counts = results.rowcount
                    trace.print(f'results.rowcount: {counts}', tracing)
                except Exception as ex:
                    pass

            trace.print(f'counts: {counts}', tracing)
            trace.print(f'execute update script executed successfully,', tracing)
            return counts
        except Exception as ex:
            trace.print(f'execute update script failed,', tracing)
            raise Exception(ex)

        #######################################
        
    def drop_table(self, schemaname, tblname, tracing = False):
        """Prepares the sql statement to drop a table and drops the table.
        
        Parameters:
            schemaname (str): schema name
            tblname (str): table name

        Returns:
            b (boolean): returns status whether table droped or not
        """
        try:
            trace.print(f'''drop table, ''', tracing)
            
            sql = f"""IF  EXISTS (
                SELECT * FROM sys.objects 
                WHERE object_id = OBJECT_ID(N'{schemaname}.{tblname}')
                AND type in (N'U'))
                DROP TABLE {schemaname}.{tblname}"""
            trace.print(text(sql), tracing)
            
            b = False
            with self.__engine.connect().execution_options(autocommit = True) as connection:
                try:
                    connection.execute(text(sql))
                    b = True
                except Exception as ex:
                    raise Exception(ex)
                
            trace.print(f'drop table executed successfully,', tracing)
            return b
        except Exception as ex:
            trace.print(f'drop table failed,', tracing)
            raise Exception(ex)

    def execute_script(self, script, tracing = False):
        """It executes the sql script provided.
        
        Parameters:
            script (str): sql script
            is_result (boolean): do you need the scalar result of connection.execute(script)?

        Returns: 
            counts (scalar or number of records) : bydeafault counts = 0 which means script executed succesfully
            , counts = -2 which means some exception occured
            , otherwise  scalar result
        """
        trace.print(f'''execute script, ''', tracing)
        trace.print(text(script), tracing)
        counts = 0
        try:
            with self.__engine.connect().execution_options(autocommit = True) as connection:
                results = connection.execute(text(script))
            
            try:
                counts = results.rowcount
                trace.print(f'results.rowcount: {counts}', tracing)
            except Exception as ex:
                counts = -2
                pass

            trace.print(f'counts: {counts}', tracing) 
            trace.print(f'execute script executed successfully,', tracing) 
            return counts  
        except Exception as ex:
            trace.print(f'execute script executed failed,', tracing)
            raise Exception(ex)
    
    def load_df_intotable(self, df, schema_name, table_name, replace_append, tracing = False):
        """It loads the dataframe into a sql table. First it drops the table if exists and creates it again. Then loads the table with dataframe.
        
        Parameters:
            schemaname (str): schema name
            tbl_name (str): table name

        Returns: 
            Nothing
        """
        is_df_loaded = False
        try:
            trace.print(f'''load df into table, ''', tracing)
            if replace_append == 'r':
                do = 'replace'
            elif replace_append == 'a':
                do = 'append'
            else:
                do = 'append'

            with self.__engine.connect() as connection:
                df.to_sql(table_name
                          , connection
                          , schema = schema_name
                          , if_exists = do
                          , chunksize = 10000
                          , index = False)
            is_df_loaded = True
            trace.print(f'load df into table executed successfully : {schema_name}.{table_name}', tracing)
            return is_df_loaded
        except Exception as ex:
            trace.print(f'load df into table failed : {schema_name}.{table_name}', tracing)
            raise Exception(ex)
    