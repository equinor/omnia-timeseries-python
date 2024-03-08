# Omnia Timeseries Python API

Python package for interacting with the [Omnia Industrial IoT Timeseries API](https://github.com/equinor/OmniaPlant/wiki).

## How do I get set up? ###

To use the Python package, install it in the following manner:

```
$ pip install git+https://github.com/equinor/omnia-timeseries-python.git@main
```

For support, create an issue on GitHub.

### Development

To start developing the package, install it in editable mode:

```
$ git clone https://github.com/equinor/omnia-timeseries-python
$ cd omnia-timeseries-python
$ pip install -e .
```

## Example usage

### Preparing Azure authentication

See https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization for general information about Timeseries API authentication and authorization.

#### With service principal credentials

```python
from azure.identity import ClientSecretCredential
import os
credential = ClientSecretCredential(
    tenant_id= "3aa4a235-b6e2-48d5-9195-7fcf05b459b0",
    client_id=os.environ['AZURE_CLIENT_ID'],
    client_secret=os.environ['AZURE_CLIENT_SECRET']
)
```

#### With user impersonation

For testing user impersonation you can use our public client ids:

- 67da184b-6bde-43fd-a155-30ed4ff162d2 (test)
- 141369bd-3dca-4b55-825b-56ad4a69b1fc (production)

```python
from azure.identity import DeviceCodeCredential
import os
credential = DeviceCodeCredential(
    tenant_id= "3aa4a235-b6e2-48d5-9195-7fcf05b459b0",
    client_id=os.environ['AZURE_CLIENT_ID']
)
```

During authentication, this will display a URL to visit, and a code to enter. After completing
the flow, execution will proceed.

#### With default credentials (azure cli, MSI and so on)

```python
from omnia_timeseries import TimeseriesEnvironment, TimeseriesAPI
from azure.identity import DefaultAzureCredential
cred = DefaultAzureCredential()
api = TimeseriesAPI(cred, TimeseriesEnvironment.Prod())
api.get_timeseries(limit=1)
```

### Getting latest datapoint for timeseries within the Test environment

```python
from omnia_timeseries import TimeseriesAPI, TimeseriesEnvironment
api = TimeseriesAPI(
    azure_credential=credential,
    environment=TimeseriesEnvironment.Test()
)
data = api.get_latest_datapoint(id='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', beforeTime='2021-02-01T09:54:30Z')
print(data['data'])

```

### Using a custom API environment

```python
api = TimeseriesAPI(
    azure_credential=credential,
    environment=TimeseriesEnvironment(
        resource_id="<azure-resource-id>",
        base_url="<base-url-for-api>"
    )
)
```

#### Output

```
>> {'items': [{'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'datapoints': [{'time': '2021-02-01T09:54:05.4200000Z', 'value': -0.000286102294921875, 'status': 192}]}]}
```

### Other use cases

Please consult the [API Reference](https://api.equinor.com/docs/services/Timeseries-api-v1-7) for a full overview of the API endpoints.
