import json

from influxdb_client import Dialect, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxQueryClient:
    
    '''
    Initialize defaults.
    Usage: client = InfluxClient(influx_server, influx_token, org_name, bucket_name)
    Example:
        client = InfluxClient("http://localhost:8086", "KlXfBqa0uSGs0icfE", "org", "bucket")
        client.write_data(data)
    '''
    def __init__(self, url, token, org, bucket, query): 
        self._org = org
        self._bucket = bucket
        self._query = query
        self._client = InfluxDBClient(url=url, token=token, org=org)
        
    def query_csv_full(self, query):
        '''
        query to csv full
        '''
        # Query: using CSV iterator
        csv_iterator = self._client.query_api().query_csv(query)

        # Serialize to values
        output = csv_iterator.to_values()
        return output

    def query_to_csv(self, query):
        '''
        query to csv
        '''
        # Query: using CSV iterator
        csv_iterator = self._client.query_api().query_csv(query,
                                                    dialect=Dialect(header=False, annotations=[]))

        for csv_line in csv_iterator:
            return csv_line
    def query_to_json(self, query):
        '''
        query to JSON
        '''
        # Query: using Table structure
        tables = self._client.query_api().query(query)

        # Serialize to JSON
        output = tables.to_json(indent=5)

        # Convert output to JSON
        result = json.loads(output)

        return result

    def query_to_column(self, query, list_columns):
        '''
        query to column
        '''
        # Query: using Table structure
        tables = self._client.query_api().query(query)

        # Serialize to values
        output = tables.to_values(columns=list_columns)
        return output


