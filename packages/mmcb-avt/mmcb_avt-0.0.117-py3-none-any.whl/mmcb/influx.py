#!/usr/bin/env python3
"""
Adapted from:

https://gitlab.ph.liv.ac.uk/avt/atlas-itk-pmmcb/-/blob/main/packaging/src/
    mmcb/sense.py

and:

https://gitlab.ph.liv.ac.uk/manex/cleanroom-environmental-monitoring-system/
    -/blob/main/Liverpool_REMS_IoT_2022-11-25/SHT85_serial_read_influxdb.py
"""

import argparse
import os
import time

from influxdb_client.client.write_api import WriteApi, SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions

from mmcb import test_environment as te


##############################################################################
# command line option handler
##############################################################################


def check_file_exists(filename):
    """
    check if file exists

    --------------------------------------------------------------------------
    args
        val : string
            filename, e.g. 'config.txt'
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError(f'{filename}: file does not exist')

    return filename


def check_arguments():
    """
    Handle command line options.

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns : class argparse.ArgumentParser
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Environmental sensing script that leverages the code\
        originally written for the ATLAS inner tracker (ITK) pixels\
        multi-module cycling box logging script. Logs various parameters\
        including temperature, humidity and pressure from various sensors.\
        Sensors are connected by I2C in the current test setup, mostly via\
        Qwiic I2C multiplexer(s). This script will run continuously until\
        terminated.'
    )
    parser.add_argument(
        'config_filename',
        nargs=1,
        metavar='configuration file',
        help='Specify the file containing the test setup configuration.',
        type=check_file_exists,
        default=None,
    )

    return parser.parse_args()


##############################################################################
def main():
    """
    Acquire data, send to influxdb
    """
    args = check_arguments()

    ##########################################################################
    # influxdb oss initialisation
    ##########################################################################

    oss_url = 'http://138.253.48.88:8086'
    oss_token = 'gtWbY-DSA8NgaPyr_pEGQwf0W7T__2YcvQwmYoPGsU-7Tuvyz2dD1PfYGM7juGj3iAPZd6YNX2s9lX-FOL9Iiw=='
    oss_org = 'UoL_environmental_monitoring'
    oss_bucket = 'REMS'
    oss_client = InfluxDBClient(url=oss_url, token=oss_token, org=oss_org)

    ##########################################################################
    # influxdb cloud initialisation
    ##########################################################################

    cloud_token = 'e54n689WZqkIepfjp5pn1tMYqg9Dy_itZhYIqwiMwn8fROnXtNAIw00rAUtHSHIvd61D65ob4HHCo_EWBHTsMA=='
    cloud_org = 'm.ormazabal-arregi@liverpool.ac.uk'
    cloud_url = 'https://europe-west1-1.gcp.cloud2.influxdata.com'
    cloud_bucket = 'rems'
    cloud_client = InfluxDBClient(url=cloud_url, token=cloud_token, org=cloud_org)

    ##########################################################################
    # acquire sensor data, send to influxdb
    ##########################################################################

    testenv = te.TestEnvironment(args.config_filename[0])

    while True:
        measurements = testenv.read_all_sensors()

        # don't process the dict if it only contains a timestamp
        if len(measurements) > 1:
            json_body = [
                {
                    'measurement': 'Environmental data',
                    'tags': {'Device': 'SOME_NODE'},
                    'fields': measurements,
                }
            ]

            print(json_body)

            # write_api_oss = oss_client.write_api(write_options=SYNCHRONOUS)
            # write_api_oss.write(oss_bucket, oss_org, json_body)
            # write_api_cloud = cloud_client.write_api(write_options=SYNCHRONOUS)
            # write_api_cloud.write(cloud_bucket, cloud_org, json_body)

        time.sleep(5)


##############################################################################
if __name__ == "__main__":
    main()
