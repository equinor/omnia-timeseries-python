# Omnia Timeseries Python API

Python package for interacting with the [Omnia Industrial IoT Timeseries API](https://github.com/equinor/OmniaPlant/wiki).

## How do I get set up? ###

To use the Python package, install it in the following manner:

```
pip install git+https://github.com/equinor/omnia-timeseries-python.git@main
```

For support, create an issue on GitHub.

## Example usage

For fundamental questions please refer to the MSAL documentation which has [code examples for multiple programming languages and scenarios](https://learn.microsoft.com/en-us/entra/identity-platform/sample-v2-code?tabs=apptype).

You should also familiarize yourself with the [azure.identity](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python) package, which we will use below.

Follow [usage examples](https://github.com/equinor/omnia-timeseries-python/blob/main/examples/usage_examples.ipynb) to learn how to retrieve data in `Json` format.  
Follow [get data as protobuf example](https://github.com/equinor/omnia-timeseries-python/blob/main/examples/get_data_protobuf.ipynb) to learn how to retrieve data in `Protobuf` format.

### Preparing Azure authentication

Read https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization to familiarize yourself with how Timeseries API handles authentication and authorization.

The `TimeseriesAPI` client accepts any `azure.identity` credential that inherits from `MsalCredential`, so you can pick the flow that suits your environment. The options we currently cover are:

- **Service principal with client secret** (`ClientSecretCredential`) for headless service-to-service scenarios.
- **Service principal with certificate** (`ClientCertificateCredential`) when you prefer cert-based authentication instead of a secret.
- **Managed identities / default credential chain** (`ManagedIdentityCredential` or `DefaultAzureCredential`) when running inside Azure.
- **Interactive browser login** (`InteractiveBrowserCredential`) for local development where you can complete the sign-in with a browser.
- **User impersonation** (`DeviceCodeCredential` or other interactive flows that acquire a user token) when you need to act on behalf of a signed-in user; this requires the Timeseries API app to consent to the `user_impersonation` scope.
- **On-behalf-of flow** (`OnBehalfOfCredential`) when a middle-tier service needs to exchange a signed-in user's token for a Timeseries API token and act with delegated permissions.

The supported credential setups are shown below.

#### With service principal credentials (client secret)

Read [Service-to-service using a shared secret](https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization#service-to-service-using-a-shared-secret) and ensure prerequisite steps have been done.

```python
from azure.identity import ClientSecretCredential
import os
credentials = ClientSecretCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID'],
    client_secret=os.environ['AZURE_CLIENT_SECRET']
)
```

#### With service principal credentials (client certificate)

Use a certificate instead of a shared secret when you want a stronger identity proof and avoid storing plain secrets.

```python
from azure.identity import ClientCertificateCredential
import os
credentials = ClientCertificateCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID'],
    certificate_path=os.environ['AZURE_CLIENT_CERT_PATH']
)
```

#### With interactive browser login

When developing locally, you can open a browser window and sign in manually.

```python
from azure.identity import InteractiveBrowserCredential
import os
credentials = InteractiveBrowserCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID']
)
```

#### With user impersonation (device code)

Use a device code or other interactive credential that requests the `user_impersonation` scope so the signed-in user is impersonated by the Timeseries API.

```python
from azure.identity import DeviceCodeCredential
import os
credentials = DeviceCodeCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID']
)
```

#### With managed / default credentials

Read [Managed Service Identity (For Equinor applications in Azure)](https://github.com/equinor/OmniaPlant/wiki/Authentication-&-Authorization#managed-service-identity-for-equinor-applications-in-azure) and ensure prerequisite steps have been done.

```python
from azure.identity import DefaultAzureCredential
credentials = DefaultAzureCredential()
```

#### With on-behalf-of flow

Use `OnBehalfOfCredential` when a backend service receives a user token (the user assertion) and needs to call the Timeseries API on that user's behalf.

```python
from azure.identity import OnBehalfOfCredential
import os
credentials = OnBehalfOfCredential(
    tenant_id=os.environ['AZURE_TENANT_ID'],
    client_id=os.environ['AZURE_CLIENT_ID'],
    client_secret=os.environ['AZURE_CLIENT_SECRET'],
    user_assertion=os.environ['USER_ASSERTION']
)
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
