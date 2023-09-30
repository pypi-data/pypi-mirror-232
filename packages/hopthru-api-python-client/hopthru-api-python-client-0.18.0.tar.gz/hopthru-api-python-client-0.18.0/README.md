# Hopthru API Python Client

This is the Hopthru API Python Client for uploading APC data to Hopthru. 

It provides the interface for determining which dates Hopthru expects to receive data for, 
and for uploading data to Hopthru.

## Uploading Correlated APC Data

The following example shows how to upload correlated APC data to Hopthru.
```python
import hopthruclient

AGENCY_NAME = 'example'
API_KEY = '<obtained from hopthru>'

def get_ridership(start_date, end_date, output_filename):
    # Implement agency-specific logic here.
    # It should write a CSV file to the path specified in output_filename.
    pass

if __name__ == '__main__':
    hopthruclient.run(get_ridership, AGENCY_NAME, API_KEY)
```

The hopthruclient.run function handles command line arguments,
connects to the Hopthru API, and determines which date ranges need to be
uploaded. It then calls the get_ridership() function provided by the script
for each date range, and uploads the file it creates. And it logs the output
so the script can be run as a scheduled task.

The agency name is used to name the folder in which the CSV files are saved
(agency_hopthru_data), the individual data files (agency_apc_start_end.csv),
and the log file (agency_hopthru_log.txt). The data folder and log file are
created in the current working directory.

## Uploading Raw APC Data

The following example shows how to upload raw APC data to Hopthru.
```python
from hopthru_api_client.apc_data import upload_raw_apc_data

AGENCY_NAME = 'example'
API_KEY = '<obtained from hopthru>'

def get_ridership(start_date, end_date, output_filename):
    # Implement agency-specific logic here.
    # It should write a CSV file to the path specified in output_filename.
    pass

if __name__ == '__main__':
    upload_raw_apc_data(
        agency_name="example",
        api_key="api-key",
        apc_data_func=get_ridership,
    )
```
By default, the upload_raw_apc_data function will query the Hopthru API for
the range of dates that need to be uploaded. It will then initiate the upload
and lastly perform the upload.

Alternatively, you can specify the start and end dates manually.

The agency name is used to name the folder in which the CSV files are saved
(agency_hopthru_data), the individual data files (agency_apc_start_end.csv),
and the log file (agency_hopthru_log.txt). The data folder and log file are
created in the current working directory.


## Building this package

- Create a virtual environment
    - `python -m venv venv`  
- Install the Python dependencies:
    - `python -m pip install --upgrade pip`
    - `python -m pip install -r test-requirements.txt`
- Build the distribution:
    - `python -m build`
- The distribution will be in the dist folder.
