.. RestSQL documentation master file, created by
   sphinx-quickstart on Wed Aug 11 10:00:46 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RestSQL's documentation!
===================================
In some cases, when facing different business or data stream queries, it is necessary to avoid the difficulty of querying data due to different query syntax. At the same time, it is also necessary to manage user rights and open some tables and fields. Therefore, as a custom configuration query statement tool, RestSQL hides the query details of multiple data sources and simplifies query work.Before use, you need to configure the target data source and specify the corresponding database connection parameters. Then use a custom Restsql statement to query the configuration database.
The tool supports data sources such as Postgre SQL, Druid, Elasticsearch, etc.

It can support API query and provide Grafana query data source.

The json query example is as follows.
::

   {
     "from":"",
     "time":{
       "column":"",
       "begin":"",
       "end":"",
       "interval":""
     },
     "select":[
       {
         "column":"",
         "alias":"",
         "metric":""
       }
     ],
     "where":[
       {
         "column":"",
         "op":"",
         "value":""
       },
       {
         "column":"",
         "op":"",
         "value":""
       }
     ],
     "group":[],
      "limit":1000
   }

.. toctree::
   :maxdepth: 10
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
