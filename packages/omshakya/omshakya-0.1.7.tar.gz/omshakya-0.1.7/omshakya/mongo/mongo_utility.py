
# ### these both syntax works fine
#from omshakya._sharedcode import _mongodbops as __sqlo
from .. _bin_cc_or_sc import _mongodbops as __mongo
from .. _bin_cc_or_sc import __version__ as __v
__version__ = __v.__VERSION__


def check_connection(cs_mongodb_url, tracing = False):
    """
    Check the connection to the mongodb database.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        str: The staus of connection.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.check_connection(tracing)

def generate_sample_data(cs_mongodb_url, db, tracing = False):
    """
    Generate the sample data in the mongodb database.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        db (str): the name of the database, it will be created if does not exists
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        List(str): The list of collection names created with sample data.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.generate_sample_data(db, tracing)

def insert_df_into_collection(cs_mongodb_url, df, db, collection, tracing = False):
    """
    Insert pandas datafrom into mongodb database collection.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        df (pandas dataframe): pandas dataframe
        db (str): the name of the database, it will be created if does not exists
        collection (str): the name of the collection, it will be created if does not exists
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        True/False: 'True' if datafrae inserted into collection else 'False'
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.insert_df_into_collection(df, db, collection, tracing)

def join_collections_into_df(cs_mongodb_url, list_coll_details, list_how, list_on, tracing = False):
    """
    Joins multiple collections in mongodb database. This is like 'sql join' or 'mongodb lookup' functionality.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        list_coll_details (List(Dict)): list of dictionaries to provide collections details
        list_how (List(str)): how to join the collections, 'left', 'right', 'inner' etc.
        list_on (List(str)): on which columns the join will be performed
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        df (pandas dataframe): the output pandas dataframe after joining collections.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.join_collections_into_df(list_coll_details, list_how, list_on, tracing)

def querycollection(cs_mongodb_url, db, collection, query, projection, tracing = False):
    """
    Query the mongodb database collection.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        db (str): the name of the database, it will be created if does not exists
        collection (str): the name of the collection, it will be created if does not exists
        query (dict): the mongodb query
        projection (dict): the mongodb projection
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        cursor: the output of mongodb query as cursor.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.querycollection(db, collection, query, projection, tracing)

def querycollection_into_df(cs_mongodb_url, db, collection, query, projection, tracing = False):
    """
    Query the mongodb database collection into the pandas dataframe.
    
    Parameters:
        cs_mongodb_url (str): the mongodb url to connect with, ex. "mongodb://localhost:27017"
        db (str): the name of the database, it will be created if does not exists
        collection (str): the name of the collection, it will be created if does not exists
        query (dict): the mongodb query
        projection (dict): the mongodb projection
        tracing (boolean): True/False, whether to print the progress of the function code execution

    Returns: 
        df (pandas dataframe): the output of mongodb query into pandas dataframe.
    Example:
        See the documentation at 'https://www.linkedin.com/company/omshakya-a-python-package/?viewAsMember=true'
    """
    __obj = __mongo.MongodbOpsWrapper(cs_mongodb_url)
    return __obj.querycollection_into_df(db, collection, query, projection, tracing)

