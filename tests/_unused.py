# class AzureAuthenticator:
#     def __init__(self, azure_credential):
#         self._azure_credential = azure_credential

#     def get_token(self, resource_id: str) -> str:
#         auth_endpoint = (
#             "https://management.azure.com/.default"
#             if "azureml" in resource_id.lower()
#             else f"{resource_id}/.default"
#         )

#         token = self._azure_credential.get_token(auth_endpoint)
#         return token.token


# class HttpClient:
#     def __init__(self, azure_credential: MsalCredential, resource_id: str):
#         self._azure_credential = azure_credential
#         self._resource_id = resource_id

#     def request(
#         self,
#         request_type: RequestType,
#         url: str,
#         accept: ContentType = "application/json",
#         payload: Optional[Union[TypedDict, dict, list]] = None,
#         params: Optional[Dict[str, Any]] = None
#     ) -> Any:

#         access_token = self._azure_credential.get_token(
#             f'{self._resource_id}/.default'
#         )

#         headers = {
#             'Authorization': f'Bearer {access_token.token}',
#             'Content-Type': 'application/json',
#             'Accept': accept,
#             'User-Agent': f'Omnia Timeseries SDK/{version} {system_version_string}'
#         }

#         print(f"Access token: {access_token.token}")
#         return _request(request_type=request_type, url=url, headers=headers, payload=payload, params=params)

