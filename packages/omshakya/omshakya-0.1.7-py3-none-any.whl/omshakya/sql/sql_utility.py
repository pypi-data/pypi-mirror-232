
# ### these both syntax works fine
#from omshakya._sharedcode import _sqloperations as __sqlo
from .._bin_cc_or_sc import _sqlops as __sqlo
from .. _bin_cc_or_sc import __version__ as __v
__version__ = __v.__VERSION__


def check_connection(cs_odbc_url, tracing = False):
    """
    Check the connection to the sql server.
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        str: The staus of connection.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.check_connection(tracing)

def select_from_sql(cs_odbc_url, script, tracing = False):
    """
    Check the connection to the sql server.
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        script (str): the microsoft sql select statement, can be any kind of select statement ex. select with 
            subqueries, select with CTE, select from views, select from function.
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        str: The staus of connection.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.select_by_script(script, tracing)

def execute_update_sql_script(cs_odbc_url, script, tracing = False):
    """
    Execute the microsoft sql update statement.
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        script (str): the microsoft sql update statement
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        count (int): The nuber of records affected by update statement.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.execute_updatescript(script, tracing)

def drop_table(cs_odbc_url, schemaname, tblname, tracing = False):
    """
    Drop the table from microsoft sql databse.
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        schemaname (str): the microsoft sql database schema name
        tblname (str): the microsoft sql database table name
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        True/False: 'True' if table was deleted else 'False'.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.drop_table(schemaname, tblname, tracing)

def execute_script(cs_odbc_url, script, tracing = False):
    """
    Execute the microsoft sql script (T-SQL). Can execute any (UPDATE, DELETE, TRUNCATE), DDL ,DCL, Stored procedures without parameters,
    SQL queries/commands except SELECT & DELETE
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        script (str): the microsoft sql script, Can be any (UPDATE, DELETE, TRUNCATE), DDL ,DCL, 
            Stored procedures without parameters. T-SQL queries/commands except SELECT & DELETE

        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        int: scalar integer result or number of rows affected. -2 means it has failed.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.execute_script(script, tracing)

def load_df_intotable(cs_odbc_url, df, schema_name, table_name, replace_append, tracing = False):
    """
    Load pandas dataframe into microsoft sql databse table.
    
    Parameters:
        cs_odbc_url (str): the microsoft sql server odbc connection string also known as odbc url
        df (pandas dataframe): the pandas dataframe to load into sql database table
        schema_name (str): the schema name ex. 'dbo'
        table_name (str): the table name ex. 'employee_table'
        replace_append (str): whether to append or replace, 'a' for append & 'r' for replace
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        True/False: 'True' if table was deleted else 'False'.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __sqlo.SqlOpsWrapper(cs_odbc_url)
    return __obj.load_df_intotable(df, schema_name, table_name, replace_append, tracing)