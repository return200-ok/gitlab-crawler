import concurrent.futures
import io
import multiprocessing
import os
from collections import OrderedDict
from csv import DictReader
from datetime import datetime
from multiprocessing import Value
from urllib.request import urlopen

import reactivex as rx
from gitlab_collector import *
from influx_client import *
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import WriteType
from reactivex import operators as ops

influx_token = os.getenv('INFLUX_TOKEN')
influx_server = os.getenv('INFLUX_DB')
org_name = os.getenv('INFLUX_ORG')
bucket_name = os.getenv('BUCKET_NAME')

class ProgressTextIOWrapper(io.TextIOWrapper):
    """
    TextIOWrapper that store progress of read.
    """
    def __init__(self, *args, **kwargs):
        io.TextIOWrapper.__init__(self, *args, **kwargs)
        self.progress = None
        pass

    def readline(self, *args, **kwarg) -> str:
        readline = super().readline(*args, **kwarg)
        self.progress.value += len(readline)
        return readline


class InfluxDBWriter(multiprocessing.Process):
    """
    Writer that writes data in batches with 50_000 items.
    """
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.client = InfluxDBClient(url=influx_server, token=influx_token, org=org_name)
        self.write_api = self.client.write_api(
            write_options=WriteOptions(write_type=WriteType.batching, batch_size=50_000, flush_interval=10_000))

    def run(self):
        while True:
            next_task = self.queue.get()
            if next_task is None:
                # Poison pill means terminate
                self.terminate()
                self.queue.task_done()
                break
            self.write_api.write(bucket=bucket_name, record=next_task)
            self.queue.task_done()

    def terminate(self) -> None:
        proc_name = self.name
        print()
        print('Writer: flushing data...')
        self.write_api.close()
        self.client.close()
        print('Writer: closed'.format(proc_name))

def init_counter(counter, progress, queue):
    """
    Initialize shared counter for display progress
    """
    global counter_
    counter_ = counter
    global progress_
    progress_ = progress
    global queue_
    queue_ = queue


def write_multiprocess(data_point):
    """
    Create multiprocess shared environment
    """
    queue_ = multiprocessing.Manager().Queue()
    counter_ = Value('i', 0)
    progress_ = Value('i', 0)
    client = InfluxClient(influx_server, influx_token, org_name, bucket_name)

    """
    Start writer as a new process
    """
    writer = InfluxDBWriter(queue_)
    writer.start()

    """
    Create process pool for parallel encoding into LineProtocol
    """
    cpu_count = multiprocessing.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(cpu_count, initializer=init_counter,
                                                initargs=(counter_, progress_, queue_)) as executor:
        
        """
        Write data into InfluxDB
        """
        executor.submit(client.write_data, data_point)

    """
    Terminate Writer
    """
    queue_.put(None)
    queue_.join()

    

    # """
    # Querying 10 pickups from dispatching 'B00008'
    # """
    # query = 'from(bucket:"my-bucket")' \
    #         '|> range(start: 2019-01-01T00:00:00Z, stop: now()) ' \
    #         '|> filter(fn: (r) => r._measurement == "taxi-trip-data")' \
    #         '|> filter(fn: (r) => r.dispatching_base_num == "B00008")' \
    #         '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")' \
    #         '|> rename(columns: {_time: "pickup_datetime"})' \
    #         '|> drop(columns: ["_start", "_stop"])|> limit(n:10, offset: 0)'

    # client = InfluxDBClient(url=influx_server, token=influx_token, org=org_name)
    # result = client.query_api().query(query=query)

    # """
    # Processing results
    # """
    # print()
    # print("=== Querying 10 pickups from dispatching 'B00008' ===")
    # print()
    # for table in result:
    #     for record in table.records:
    #         print(
    #             f'Dispatching: {record["dispatching_base_num"]} pickup: {record["pickup_datetime"]} dropoff: {record["dropoff_datetime"]}')

    """
    Close client
    """
    # client.close()
