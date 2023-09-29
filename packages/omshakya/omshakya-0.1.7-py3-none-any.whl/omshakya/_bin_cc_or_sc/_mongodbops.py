import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from pymongo import MongoClient
from . _traceprinter import TracerPrinterWrapper as trace
import datetime
from dateutil import parser

class MongodbOpsWrapper:
    '''This class interacts with mongodb and performs mongodb operations.'''
        
    '''This class interacts with sql and performs sql operations.'''
    def __init__(self, cs_mongodb_url):
        #url = "mongodb://localhost:27017"
        mongoclient = MongoClient(cs_mongodb_url)
        #print(f'oms traces, mongodb connected,')
        self.__client = mongoclient
    
    def __del__(self):
        #print("oms traces, mongodb obj being automatically destroyed,")
        pass


    def check_connection(self, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        refer: https://www.mongodb.com/docs/manual/reference/method/db.collection.find/
        """
        trace.print(f'check mongodb connection,', tracing)
        status = 'mongodb connection failed.'
        try:
            _ = self.__client.list_databases()

            status = 'mongodb connection succeeded.'
            trace.print(f'check mongodb connection executed,', tracing)
        except Exception as ex:
            status = 'mongodb connection failed.'
            trace.print(f'mongodb connection failed,', tracing)
            raise Exception(ex)
        return status
    
    def querycollection(self, db, collection, query, projection, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        refer: https://www.mongodb.com/docs/manual/reference/method/db.collection.find/
        """
        try:
            trace.print(f'''query collection, db: {db}
                        \t, collection: {collection}
                        \t, query: {query}
                        \t, projection: {projection}''', tracing)

            db = self.__client[db]
            if query is None:
                q = {}
            else:
                q = query
            
            if projection is None:
                collection = db.get_collection(collection).find(q)
            else:
                collection = db.get_collection(collection).find(q, projection)

            trace.print(f'query collection executed,', tracing)
            return collection
        except Exception as ex:
            trace.print(f'query collection failed,', tracing)
            raise Exception(ex)
    
    def querycollection_into_df(self, db, collection, query, projection, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        """
        try:
            trace.print(f'''query collection into df,''', tracing)
            results = self.querycollection(db, collection, query, projection, tracing)

            df = pd.DataFrame(list(results))
            trace.print(f'query collection into df executed,', tracing)

            return df
        except Exception as ex:
            trace.print(f'query collection into df failed,', tracing)
            raise Exception(ex)
 
    def insert_df_into_collection(self, df, db, collection, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        """

        b = False
        trace.print(f'insert df into db: {db}, collection: {collection}', tracing)
        try:
            db = self.__client[db]
            
            # df.reset_index(inplace = True) #if you need a default index
            data_dict = df.to_dict("records")
            collection = db[collection]

            collection.insert_many(data_dict)
            trace.print(f'df inserted into {db}.{collection} executed successfully,', tracing)
            b = True
            return b
        except Exception as ex:
            trace.print(f'insert df failed,', tracing)
            raise Exception(ex)

    def join_collections_into_df(self, list_coll_details, list_how, list_on, tracing = False):
        """It executes the select sql statement provided as sql query.
        
        Parameters:
            query (str): sql query to select data

        Returns: 
            df (dataframe): returns dataframe
        """
        try:
            trace.print(f'joining collections...', tracing)

            list_df = []
            for d in list_coll_details:
                df = self.querycollection_into_df(d.get('db'),
                                                d.get('coll'),
                                                None,
                                                d.get('project'),
                                                tracing
                                                )
                list_df.append(df)

            no_of_joins = len(list_df) - 1
            
            if no_of_joins > 0:
                dfj = list_df[0].merge(list_df[1]
                                    , how = list_how[0]
                                    , left_on = list_on[0].get('left_on')
                                    , right_on = list_on[0].get('right_on'))
                
                if no_of_joins > 1:
                    for i in range(1, no_of_joins):
                        dfj = dfj.merge(list_df[i+1]
                                        , how = list_how[i]
                                        , left_on = list_on[i].get('left_on')
                                        , right_on = list_on[i].get('right_on')
                                        )
            
            trace.print(f'joining collections executed,', tracing)
            return dfj
        except Exception as ex:
            trace.print(f'joining collections failed,', tracing)
            raise Exception(ex)

    def generate_sample_data(self, db, tracing = False):
        try:
            # ### prepare some sample data first
            registration_date = '2023-07-11T00:00:00.000Z'
            registration_date = parser.parse(registration_date)
            dt = datetime.datetime.now(tz = datetime.timezone.utc)

            data = [{"name" : "om", "course" : "SQL", "fees" : 265, "currency" : "usd", "add" : {"state": "up", 'country':'india'}, "reg_date": datetime.datetime(2009, 11, 12, 11, 14) },
                    {"name" : "om shakya", "course" : "SQL", "fees" : 270, "currency" : "usd", "add" : {"state": "ny", 'country':'america'}, "reg_date" : registration_date },
                    {"name" : "om prakash shakya", "course" : "python", "fees" : 250, "currency" : "inr", "add" : {"state": "delhi", 'country':'india'}, "reg_date" : parser.parse('2023-07-11 10:12:36')},
                    {"name" : "kanika", "course" : "python", "fees" : 250, "currency" : "inr", "add" : {"state": "delhi", 'country':'india'}, "reg_date" : dt},
                    {"name" : "alex", "course" : "SQL", "fees" : 275, "currency" : "inr", "add" : {"state": "delhi", 'country':'india'}, "reg_date" : dt},
                    {"name" : "James", "course" : "pyspark", "fees" : 285, "currency" : "usd", "add" : {"state": "ny", 'country':'america'}, "reg_date" : dt},
                    {"name" : "Joseph", "course" : "SQL", "fees" : 290, "currency" : "usd", "add" : {"state": "al", 'country':'america'}, "reg_date" : dt},
                    {"name" : "Elizabeth", "course" : "python", "fees" : 240, "currency" : "usd", "add" : {"state": "fs", 'country':'america'}, "reg_date" : dt},
                    {"name" : "Noah", "course" : "SQL", "fees" : 278, "currency" : "inr", "sg" : {"state": "delhi", 'country':'singapore'}, "reg_date" : dt},
                    ]

            # ### create db & collection and insert sample data
            db = self.__client[db]
            collection = 'registrations'
            collection = db.get_collection(collection)
            collection.insert_many(data)

            # ### one more sample data
            data_curr = [{"currency" : "sd", "description" : "singapore dollar"},
                    {"currency" : "usd", "description" : "united states dollar"},
                    {"currency" : "inr", "description" : "indian rupee"},
                    {"currency" : "gbp", "description" : "great britain pound"}
                    ]
            collection = db.get_collection('currencies')
            collection.insert_many(data_curr)

            # ### one more sample data
            data_fees = [{"amount" : 250, "in words" : "two fifty"},
                         {"amount" : 260, "in words" : "two sixty"},
                         {"amount" : 270, "in words" : "two seventy"},
                         {"amount" : 275, "in words" : "two seventy five"}
                         ]
            db = self.__client['test_db']
            collection = db.get_collection('fees')
            collection.insert_many(data_fees)

            list_cols = ['registrations', 'currencies', 'fees']

            trace.print('sample data generated successfully,', tracing)
            return list_cols
        
        except Exception as ex:
            trace.print(f'sample data generation failed,', tracing)
            raise Exception(ex)

    def mongo_ops_1():
        print('mongo_ops_1')
