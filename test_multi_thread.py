"""
Import public NYC taxi and for-hire vehicle (Uber, Lyft, etc.) trip data into InfluxDB 2.0

https://github.com/toddwschneider/nyc-taxi-data
"""
import concurrent.futures
import io
import multiprocessing
from collections import OrderedDict
from csv import DictReader
from datetime import datetime
from multiprocessing import Value
from urllib.request import urlopen

import reactivex as rx
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import WriteType
from reactivex import operators as ops

influx_token = "KlXfBqa0uSGs0icfE-3g8FsQAoC9hx_QeDsxE3pn0p9wWWLn0bzDZdSmrOijoTA_Tr2MGPnF-LxZl-Nje8YJGQ=="
influx_server = "http://192.168.3.101:8086"
org_name = "org"
BUCKET_NAME = "gitlab"

# class ProgressTextIOWrapper(io.TextIOWrapper):
#     """
#     TextIOWrapper that store progress of read.
#     """
#     def __init__(self, *args, **kwargs):
#         io.TextIOWrapper.__init__(self, *args, **kwargs)
#         self.progress = None
#         pass

#     def readline(self, *args, **kwarg) -> str:
#         readline = super().readline(*args, **kwarg)
#         self.progress.value += len(readline)
#         return readline


class InfluxDBWriter(multiprocessing.Process):
    """
    Writer that writes data in batches with 50_000 items.
    """
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.client = InfluxDBClient(url=influx_server, token=influx_token, org=org_name, debug=False)
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
            self.write_api.write(bucket="test", record=next_task)
            self.queue.task_done()

    def terminate(self) -> None:
        proc_name = self.name
        print()
        print('Writer: flushing data...')
        self.write_api.close()
        self.client.close()
        print('Writer: closed'.format(proc_name))


# def parse_row(row: OrderedDict):
#     """Parse row of CSV file into Point with structure:

#         taxi-trip-data,DOLocationID=152,PULocationID=79,dispatching_base_num=B02510 dropoff_datetime="2019-01-01 01:27:24" 1546304267000000000

#     CSV format:
#         dispatching_base_num,pickup_datetime,dropoff_datetime,PULocationID,DOLocationID,SR_Flag
#         B00001,2019-01-01 00:30:00,2019-01-01 02:51:55,,,
#         B00001,2019-01-01 00:45:00,2019-01-01 00:54:49,,,
#         B00001,2019-01-01 00:15:00,2019-01-01 00:54:52,,,
#         B00008,2019-01-01 00:19:00,2019-01-01 00:39:00,,,
#         B00008,2019-01-01 00:27:00,2019-01-01 00:37:00,,,
#         B00008,2019-01-01 00:48:00,2019-01-01 01:02:00,,,
#         B00008,2019-01-01 00:50:00,2019-01-01 00:59:00,,,
#         B00008,2019-01-01 00:51:00,2019-01-01 00:56:00,,,
#         B00009,2019-01-01 00:44:00,2019-01-01 00:58:00,,,
#         B00009,2019-01-01 00:19:00,2019-01-01 00:36:00,,,
#         B00009,2019-01-01 00:36:00,2019-01-01 00:49:00,,,
#         B00009,2019-01-01 00:26:00,2019-01-01 00:32:00,,,
#         ...

#     :param row: the row of CSV file
#     :return: Parsed csv row to [Point]
#     """

#     return Point("taxi-trip-data") \
#         .tag("dispatching_base_num", row['dispatching_base_num']) \
#         .tag("PULocationID", row['PULocationID']) \
#         .tag("DOLocationID", row['DOLocationID']) \
#         .tag("SR_Flag", row['SR_Flag']) \
#         .field("dropoff_datetime", row['dropoff_datetime']) \
#         .time(row['pickup_datetime']) \
#         .to_line_protocol()


# def parse_rows(rows, total_size):
#     """
#     Parse bunch of CSV rows into LineProtocol

#     :param total_size: Total size of file
#     :param rows: CSV rows
#     :return: List of line protocols
#     """
#     _parsed_rows = list(map(parse_row, rows))

#     counter_.value += len(_parsed_rows)
#     if counter_.value % 10_000 == 0:
#         print('{0:8}{1}'.format(counter_.value, ' - {0:.2f} %'
#                                 .format(100 * float(progress_.value) / float(int(total_size))) if total_size else ""))
#         pass

#     queue_.put(_parsed_rows)
#     return None


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

def f(x='1'):
    print('x is : ', x)

if __name__ == "__main__":
    list_data_point = [1, 2, 3, 4, 5]
    """
    Create multiprocess shared environment
    """
    queue_ = multiprocessing.Manager().Queue()
    counter_ = Value('i', 0)
    progress_ = Value('i', 0)
    startTime = datetime.now()
    print(queue_, counter_, progress_)

    """
    Start writer as a new process
    """
    writer = InfluxDBWriter(queue_)
    print(writer)
    writer.start()

    """
    Create process pool for parallel encoding into LineProtocol
    """
    cpu_count = multiprocessing.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(cpu_count, initializer=init_counter,
                                                initargs=(counter_, progress_, queue_)) as executor:

        for data_point in list_data_point:
            queue_.put(data_point)
            executor.submit(f, data_point)

    """
    Terminate Writer
    """
    queue_.put(None)
    queue_.join()

    print()
    print(f'Import finished in: {datetime.now() - startTime}')
    print()

