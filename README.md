# Omnia Timeseries Python API

Python package for interacting with the [Omnia Industrial IoT Timeseries API](https://github.com/equinor/OmniaPlant/wiki).

## How do I get set up? ###

To use the Python package, install it in the following manner:

```
$ pip install git+https://github.com/equinor/omnia-timeseries-python.git@main
```

For support, create an issue on GitHub.

## Example usage

For fundamental questions please refer to the MSAL documentation which has [code examples for multiple programming languages and scenarios](https://learn.microsoft.com/en-us/entra/identity-platform/sample-v2-code?tabs=apptype).

You should also familiarize yourself with the [azure.identity](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python) package, which we will use below.

Follow [client credentials flow example](https://github.com/equinor/omnia-timeseries-python/blob/main/examples/client_secret_auth.ipynb) to learn how to retrieve data in `Json` format.  
Follow [get data as protobuf example](https://github.com/equinor/omnia-timeseries-python/blob/main/examples/get_data_protobuf.ipynb) to learn how to retrieve data in `Protobuf` format.

### Preparing Azure authentication

Please read https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization to familiarize yourself with how Timeseries API handles authentication and authorization.

We support the following authentication flows:
- Client (service principal) credentials: https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow
- User impersonation: https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow
- Managed Service Identity (MSI): https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview

The supported credential setups are shown below.

#### With service principal credentials

Read [Service-to-service using a shared secret](https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization#service-to-service-using-a-shared-secret) and ensure prerequisite steps have been done.

```python
from azure.identity import ClientSecretCredential
import os
credential = ClientSecretCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID'],
    client_secret=os.environ['AZURE_CLIENT_SECRET']
)
```

#### With user impersonation

Read [Authenticating by user impersonation without any shared secret (For people with Equinor accounts)](https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization#authenticating-by-user-impersonation-without-any-shared-secret-for-people-with-equinor-accounts) and ensure prerequisite steps have been done.

For testing user impersonation you can use our public client ids:

- 675bd975-260f-498e-82cd-65f67b34fe7d (test)
- 67da184b-6bde-43fd-a155-30ed4ff162d2 (production)

```python
from azure.identity import DeviceCodeCredential
import os
credential = DeviceCodeCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID']
)
```

During authentication, this will display a URL to visit, and a code to enter. After completing
the flow, execution will proceed.

#### With default credentials (azure cli, MSI and so on)

Read [Managed Service Identity (For Equinor applications in Azure)](https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization#managed-service-identity-for-equinor-applications-in-azure) and ensure prerequisite steps have been done.

```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

### Output

The `Json` response from Timeseries API looks like this:
```
>> {'items': [{'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'datapoints': [{'time': '2021-02-01T09:54:05.4200000Z', 'value': -0.000286102294921875, 'status': 192}]}]}
```

The `Protobuf` response from Timeseries API looks like this:
```
{ "data": [ { "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "totalCount": "1", "fields": [ "time", "value", "status" ], "values": [ { "int64": "1727263834898000000" }, { "double": 246.56092834472656 }, { "uint32": 192 } ] } ] }
```

### Other use cases

Please consult the [API Reference](https://api.equinor.com/api-details#api=Timeseries-api-v1-7) for a full overview of the API endpoints.