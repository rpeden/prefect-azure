import abc
import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING

try:
    from azure.cosmos import CosmosClient

    if TYPE_CHECKING:
        from azure.cosmos import ContainerProxy, DatabaseProxy
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

try:
    from azure.storage.blob.aio import BlobClient, BlobServiceClient, ContainerClient
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

try:
    from azureml.core.authentication import ServicePrincipalAuthentication
    from azureml.core.workspace import Workspace
except ModuleNotFoundError:
    pass  # a descriptive error will be raised in get_client

from prefect.logging import get_run_logger

HELP_URLS = {
    "blob_storage": "https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python#copy-your-credentials-from-the-azure-portal",  # noqa
    "cosmos_db": "https://docs.microsoft.com/en-us/azure/cosmos-db/sql/create-sql-api-python#update-your-connection-string",  # noqa
    "ml": "https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/manage-azureml-service/authentication-in-azureml/authentication-in-azureml.ipynb",  # noqa
}
HELP_FMT = "Please visit {help_url} for retrieving the proper connection string."


def _raise_help_msg(key):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            logger = get_run_logger()
            try:
                return func(*args, **kwargs)
            except NameError:
                logger.exception(
                    f"Using `prefect_azure.{key}` requires "
                    f"`pip install prefect_azure[{key}]`"
                )
                raise
            except ValueError:
                logger.exception(HELP_FMT.format(help_url=HELP_URLS[key]))
                raise

        return inner

    return outer


@dataclass
class AzureCredentials(abc.ABC):
    """
    Dataclass used to manage authentication with Azure. Azure authentication is
    handled via the `azure` module.
    """

    @abc.abstractmethod
    def get_client(self) -> None:
        pass


@dataclass
class BlobStorageAzureCredentials(AzureCredentials):
    @_raise_help_msg("blob_storage")
    def get_client(self) -> "BlobServiceClient":
        """
        Returns an authenticated base Blob Service client that can be used to create
        other clients for Azure services.

        Example:
            Create an authorized Blob Service session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import BlobStorageAzureCredentials

            @flow
            async def example_get_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = BlobStorageAzureCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_client() as blob_service_client:
                    # run other code here
                    pass

            asyncio.run(example_get_client_flow())
            ```
        """
        return BlobServiceClient.from_connection_string(self.connection_string)

    @_raise_help_msg("blob_storage")
    def get_blob_client(self, container, blob) -> "BlobClient":
        """
        Returns an authenticated Blob client that can be used to
        download and upload blobs.

        Args:
            container: Name of the Blob Storage container to retrieve from.
            blob: Name of the blob within this container to retrieve.

        Example:
            Create an authorized Blob session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import BlobStorageAzureCredentials

            @flow
            async def example_get_blob_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = BlobStorageAzureCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_blob_client(
                    "container", "blob"
                ) as blob_client:
                    # run other code here
                    pass

            asyncio.run(example_get_blob_client_flow())
            ```
        """
        blob_client = BlobClient.from_connection_string(
            self.connection_string, container, blob
        )
        return blob_client

    @_raise_help_msg("blob_storage")
    def get_container_client(self, container) -> "ContainerClient":
        """
        Returns an authenticated Container client that can be used to create clients
        for Azure services.

        Args:
            container: Name of the Blob Storage container to retrieve from.

        Example:
            Create an authorized Container session
            ```python
            import os
            import asyncio
            from prefect import flow
            from prefect_azure import BlobStorageAzureCredentials

            @flow
            async def example_get_container_client_flow():
                connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                azure_credentials = BlobStorageAzureCredentials(
                    connection_string=connection_string,
                )
                async with azure_credentials.get_container_client(
                    "container"
                ) as container_client:
                    # run other code here
                    pass

            asyncio.run(example_get_container_client_flow())
            ```
        """
        container_client = ContainerClient.from_connection_string(
            self.connection_string, container
        )
        return container_client


@dataclass
class CosmosDbAzureCredentials(AzureCredentials):
    @_raise_help_msg("cosmos_db")
    def get_client(self) -> "CosmosClient":
        """
        Returns an authenticated Cosmos client that can be used to create
        other clients for Azure services.

        Example:
            Create an authorized Cosmos session
            ```python
            import os
            from prefect import flow
            from prefect_azure import CosmosDbAzureCredentials

            @flow
            def example_get_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = CosmosDbAzureCredentials(
                    connection_string=connection_string,
                )
                cosmos_client = azure_credentials.get_client()
                return cosmos_client

            example_get_client_flow()
            ```
        """
        return CosmosClient.from_connection_string(self.connection_string)

    def get_database_client(self, database: str) -> "DatabaseProxy":
        """
        Returns an authenticated Database client.

        Args:
            database: Name of the database.

        Example:
            Create an authorized Cosmos session
            ```python
            import os
            from prefect import flow
            from prefect_azure import CosmosDbAzureCredentials

            @flow
            def example_get_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = CosmosDbAzureCredentials(
                    connection_string=connection_string,
                )
                cosmos_client = azure_credentials.get_database_client()
                return cosmos_client

            example_get_database_client_flow()
            ```
        """
        cosmos_client = self.get_client()
        database_client = cosmos_client.get_database_client(database=database)
        return database_client

    def get_container_client(self, container: str, database: str) -> "ContainerProxy":
        """
        Returns an authenticated Container client used for querying.

        Args:
            container: Name of the Cosmos DB container to retrieve from.
            database: Name of the Cosmos DB database.

        Example:
            Create an authorized Container session
            ```python
            import os
            from prefect import flow
            from prefect_azure import BlobStorageAzureCredentials

            @flow
            def example_get_container_client_flow():
                connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
                azure_credentials = CosmosDbAzureCredentials(
                    connection_string=connection_string,
                )
                container_client = azure_credentials.get_container_client(container)
                return container_client

            example_get_container_client_flow()
            ```
        """
        database_client = self.get_database_client(database)
        container_client = database_client.get_container_client(container=container)
        return container_client


@dataclass
class MlAzureCredentials(AzureCredentials):

    tenant_id: str
    service_principal_id: str
    service_principal_password: str
    subscription_id: str
    resource_group: str
    workspace_name: str

    @_raise_help_msg("ml")
    def get_client(self) -> "Workspace":
        """
        Returns an authenticated base Workspace that can be used in
        Azure's Datasets and Datastores.

        Example:
            Create an authorized Blob Service session
            ```python
            import os
            from prefect import flow
            from prefect_azure import MlAzureCredentials

            @flow
            def example_get_client_flow():
                azure_credentials = MlAzureCredentials(
                    "tenant_id",
                    "service_principal_id",
                    "service_principal_password",
                    "subscription_id",
                    "resource_group",
                    "workspace_name"
                )
                workspace_client = azure_credentials.get_client()
                return workspace_client

            example_get_client_flow()
            ```
        """
        service_principal_authentication = ServicePrincipalAuthentication(
            tenant_id=self.tenant_id,
            service_principal_id=self.service_principal_id,
            service_principal_password=self.service_principal_password,
        )

        workspace = Workspace(
            subscription_id=self.subscription_id,
            resource_group=self.resource_group,
            workspace_name=self.workspace_name,
            auth=service_principal_authentication,
        )

        return workspace
