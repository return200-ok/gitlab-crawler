import logging
from time import time

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS
from influxdb_client.rest import ApiException

logger = logging.getLogger(__name__)

class InfluxPoint:
    
    """Initialize defaults."""
    def __init__(self, measurement, tags, fields, timestamp=None):
        self.measurement = measurement
        self.tags = tags
        self.fields = fields
        self.timestamp = timestamp
        
        '''
        Example:
            tags = {"stock": "MSFT", "stock_id": "abc789"}
            fields = {"Open": 68, "High": 69.38, "Low": 60.13,}
            timestamp = int(time())
            data_point = InfluxPoint(measurement, tags, fields, timestamp)
        '''
        self._point = [{
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": fields
        }]

class InfluxClient:
    
    '''
    Initialize defaults.
    Usage: client = InfluxClient(influx_server, influx_token, org_name, bucket_name)
    Example:
        client = InfluxClient("http://localhost:8086", "KlXfBqa0uSGs0icfE", "org", "bucket")
        client.write_data(data)
    '''
    def __init__(self, url, token, org, bucket): 
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClient(url=url, token=token, org=org)
    
    '''
    Check connection to InfluxDb
    Example:
        client = InfluxClient(influx_server, influx_token, org_name, bucket_name)
        client.check_connection()
    '''
    def check_connection(self):
        """Check that the InfluxDB is running."""
        print("> Checking connection ...", end=" ")
        self._client.api_client.call_api('/ping', 'GET')
        print("ok")
        
    '''
    Check query to InfluxDB
    Example:
        client = InfluxClient(influx_server, influx_token, org_name, bucket_name)
        client.check_query()
    '''
    def check_query(self, query):
        """Check that the credentials has permission to query from the Bucket"""
        print("> Checking credentials for query ...", end=" ")
        query_api = self._client.query_api()
        result = query_api.query(org=self._org, query=query)
        try:
            result
        except ApiException as e:
            # missing credentials
            if e.status == 404:
                raise Exception(f"The specified token doesn't have sufficient credentials to read from '{self._bucket}' "
                                f"or specified bucket doesn't exists.") from e
            raise
        print("ok")

    def check_write(self):
        """Check that the credentials has permission to write into the Bucket"""
        print("> Checking credentials for write ...", end=" ")
        try:
            self._client.write_api(write_options=SYNCHRONOUS).write(self._bucket, self._org, b"")
        except ApiException as e:
            # bucket does not exist
            if e.status == 404:
                message = 'The specified bucket does not exist.'
                logging.exception(message)
                raise Exception(f"{message}") from e
            # insufficient permissions
            if e.status == 403:
                message = "The specified token does not have sufficient credentials to write to "+self._bucket+"."
                logging.exception(message)
                raise Exception(f"{message}") from e
            # 400 (BadRequest) caused by empty LineProtocol
            if e.status != 400:
                logging.exception(e)
                raise
        print("ok")

    '''
    Method called write_api which is used to write data into your database
    Example:
        data_point=["MSFT,stock=MSFT Open=62.79,High=63.84,Low=62.13"]
        client.write_data(data_point)
    '''
    def write_data(self, data, write_option=SYNCHRONOUS):
        write_api = self._client.write_api(write_option)
        write_api.write(self._bucket, self._org, data, write_precision='s')
    
    
    '''
    Method called delete_data used to delete data 
    Example:
        start_time = "2022-11-10T08:26:51.098Z" # type string: timestamp rfc3339
        stop_time = "2022-11-17T00:00:00.098Z"
        client.delete_data(start_time, stop_time, measurement)
    '''
    def delete_data(self, start, stop, measurement):
        delete_api = self._client.delete_api()
        self.start = start
        self.stop = stop
        delete_api.delete(start, stop, f'_measurement="{measurement}"', bucket=self._bucket, org=self._org)

    def close_process(self):
        self._client.close()

 
# start_time = "2022-11-01T00:00:00.000Z" # type string: timestamp rfc3339
# stop_time = "2022-12-08T00:00:00.000Z"
# client = InfluxClient("http://192.168.3.101:8086", "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ==", "org", "gitlab_test")
# client.delete_data(start_time, stop_time, "project")







    