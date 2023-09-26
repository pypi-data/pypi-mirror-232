from __future__ import annotations

import json
from datetime import datetime, timezone
from ssl import SSLContext
from types import TracebackType
from typing import Any

import jwt
from httpx import AsyncClient

from meilisearch_python_async._http_requests import HttpRequests
from meilisearch_python_async._utils import is_pydantic_2
from meilisearch_python_async.errors import InvalidRestriction, MeilisearchApiError
from meilisearch_python_async.index import Index
from meilisearch_python_async.models.client import (
    ClientStats,
    Key,
    KeyCreate,
    KeySearch,
    KeyUpdate,
)
from meilisearch_python_async.models.health import Health
from meilisearch_python_async.models.index import IndexInfo
from meilisearch_python_async.models.search import SearchParams, SearchResultsWithUID
from meilisearch_python_async.models.task import TaskInfo
from meilisearch_python_async.models.version import Version
from meilisearch_python_async.task import wait_for_task


class Client:
    """The client to connect to the MeilisearchApi."""

    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        *,
        timeout: int | None = None,
        verify: str | bool | SSLContext = True,
    ) -> None:
        """Class initializer.

        Args:

            url: The url to the Meilisearch API (ex: http://localhost:7700)
            api_key: The optional API key for Meilisearch. Defaults to None.
            timeout: The amount of time in seconds that the client will wait for a response before
                timing out. Defaults to None.
            verify: SSL certificates (a.k.a CA bundle) used to
                verify the identity of requested hosts. Either `True` (default CA bundle),
                a path to an SSL certificate file, or `False` (disable verification)
        """
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
        else:
            headers = None

        self.http_client = AsyncClient(
            base_url=url, timeout=timeout, headers=headers, verify=verify
        )
        self._http_requests = HttpRequests(self.http_client)

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(
        self,
        et: type[BaseException] | None,
        ev: type[BaseException] | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Closes the client.

        This only needs to be used if the client was not created with a context manager.
        """
        await self.http_client.aclose()

    async def create_dump(self) -> TaskInfo:
        """Trigger the creation of a Meilisearch dump.

        Returns:

            The details of the task.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     await client.create_dump()
        """
        response = await self._http_requests.post("dumps")

        return TaskInfo(**response.json())

    async def create_index(self, uid: str, primary_key: str | None = None) -> Index:
        """Creates a new index.

        Args:

            uid: The index's unique identifier.
            primary_key: The primary key of the documents. Defaults to None.

        Returns:

            An instance of Index containing the information of the newly created index.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.create_index("movies")
        """
        return await Index.create(self.http_client, uid, primary_key)

    async def delete_index_if_exists(self, uid: str) -> bool:
        """Deletes an index if it already exists.

        Args:

            uid: The index's unique identifier.

        Returns:

            True if an index was deleted for False if not.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     await client.delete_index_if_exists()
        """
        url = f"indexes/{uid}"
        response = await self._http_requests.delete(url)
        status = await wait_for_task(
            self.http_client, response.json()["taskUid"], timeout_in_ms=100000
        )
        if status.status == "succeeded":
            return True
        return False

    def generate_tenant_token(
        self,
        search_rules: dict[str, Any] | list[str],
        *,
        api_key: Key,
        expires_at: datetime | None = None,
    ) -> str:
        """Generates a JWT token to use for searching.

        Args:

            search_rules: Contains restrictions to use for the token. The default rules used for
                the API key used for signing can be used by setting searchRules to ["*"]. If "indexes"
                is included it must be equal to or more restrictive than the key used to generate the
                token.
            api_key: The API key to use to generate the token.
            expires_at: The timepoint at which the token should expire. If value is provided it
                shoud be a UTC time in the future. Default = None.

        Returns:

            A JWT token

        Raises:

            InvalidRestriction: If the restrictions are less strict than the permissions allowed
                in the API key.
            KeyNotFoundError: If no API search key is found.

        Examples:

            >>> from datetime import datetime, timedelta, timezone
            >>> from meilisearch_python_async import Client
            >>>
            >>> expires_at = datetime.now(tz=timezone.utc) + timedelta(days=7)
            >>>
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     token = client.generate_tenant_token(
            >>>         search_rules = ["*"], api_key=api_key, expires_at=expires_at
            >>>     )
        """
        # if Client._valid_uuid(api_key.key) is False:
        #     raise Exception("The uid must comply to the uuid4 format.")

        if isinstance(search_rules, dict) and search_rules.get("indexes"):
            for index in search_rules["indexes"]:
                if api_key.indexes != ["*"] and index not in api_key.indexes:
                    raise InvalidRestriction(
                        "Invalid index. The token cannot be less restrictive than the API key"
                    )

        payload: dict[str, Any] = {"searchRules": search_rules}

        payload["apiKeyUid"] = api_key.uid
        if expires_at:
            if expires_at <= datetime.now(tz=timezone.utc):
                raise ValueError("expires_at must be a time in the future")

            payload["exp"] = int(datetime.timestamp(expires_at))

        return jwt.encode(payload, api_key.key, algorithm="HS256")

    async def get_indexes(
        self, *, offset: int | None = None, limit: int | None = None
    ) -> list[Index] | None:
        """Get all indexes.
        Args:

            offset: Number of indexes to skip. The default of None will use the Meilisearch
                default.
            limit: Number of indexes to return. The default of None will use the Meilisearch
                default.

        Returns:

            A list of all indexes.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     indexes = await client.get_indexes()
        """
        if offset is not None and limit is not None:
            url = f"indexes?offset={offset}&limit={limit}"
        elif offset is not None:
            url = f"indexes?offset={offset}"
        elif limit is not None:
            url = f"indexes?limit={limit}"
        else:
            url = "indexes"

        response = await self._http_requests.get(url)

        if not response.json()["results"]:
            return None

        return [
            Index(
                http_client=self.http_client,
                uid=x["uid"],
                primary_key=x["primaryKey"],
                created_at=x["createdAt"],
                updated_at=x["updatedAt"],
            )
            for x in response.json()["results"]
        ]

    async def get_index(self, uid: str) -> Index:
        """Gets a single index based on the uid of the index.

        Args:

            uid: The index's unique identifier.

        Returns:

            An Index instance containing the information of the fetched index.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.get_index()
        """
        return await Index(self.http_client, uid).fetch_info()

    def index(self, uid: str) -> Index:
        """Create a local reference to an index identified by UID, without making an HTTP call.

        Because no network call is made this method is not awaitable.

        Args:

            uid: The index's unique identifier.

        Returns:

            An Index instance.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = client.index("movies")
        """
        return Index(self.http_client, uid=uid)

    async def get_all_stats(self) -> ClientStats:
        """Get stats for all indexes.

        Returns:

            Information about database size and all indexes.
            https://docs.meilisearch.com/reference/api/stats.html

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     stats = await client.get_all_stats()
        """
        response = await self._http_requests.get("stats")

        return ClientStats(**response.json())

    async def get_or_create_index(self, uid: str, primary_key: str | None = None) -> Index:
        """Get an index, or create it if it doesn't exist.

        Args:

            uid: The index's unique identifier.
            primary_key: The primary key of the documents. Defaults to None.

        Returns:

            An instance of Index containing the information of the retrieved or newly created index.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.MeilisearchTimeoutError: If the connection times out.
            MeilisearchTimeoutError: If the connection times out.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.get_or_create_index("movies")
        """
        try:
            index_instance = await self.get_index(uid)
        except MeilisearchApiError as err:
            if "index_not_found" not in err.code:
                raise
            index_instance = await self.create_index(uid, primary_key)
        return index_instance

    async def create_key(self, key: KeyCreate) -> Key:
        """Creates a new API key.

        Args:

            key: The information to use in creating the key. Note that if an expires_at value
                is included it should be in UTC time.

        Returns:

            The new API key.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> from meilissearch_async_client.models.client import KeyCreate
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     key_info = KeyCreate(
            >>>         description="My new key",
            >>>         actions=["search"],
            >>>         indexes=["movies"],
            >>>     )
            >>>     keys = await client.create_key(key_info)
        """
        if is_pydantic_2():
            response = await self._http_requests.post("keys", json.loads(key.model_dump_json(by_alias=True)))  # type: ignore[attr-defined]
        else:  # pragma: no cover
            response = await self._http_requests.post("keys", json.loads(key.json(by_alias=True)))  # type: ignore[attr-defined]

        return Key(**response.json())

    async def delete_key(self, key: str) -> int:
        """Deletes an API key.

        Args:

            key: The key or uid to delete.

        Returns:

            The Response status code. 204 signifies a successful delete.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     await client.delete_key("abc123")
        """
        response = await self._http_requests.delete(f"keys/{key}")
        return response.status_code

    async def get_keys(self, *, offset: int | None = None, limit: int | None = None) -> KeySearch:
        """Gets the Meilisearch API keys.
        Args:

            offset: Number of indexes to skip. The default of None will use the Meilisearch
                default.
            limit: Number of indexes to return. The default of None will use the Meilisearch
                default.

        Returns:

            API keys.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            from meilisearch_python_async import Client
            async with Client("http://localhost.com", "masterKey") as client:
                keys = await client.get_keys()
        """
        if offset is not None and limit is not None:
            url = f"keys?offset={offset}&limit={limit}"
        elif offset is not None:
            url = f"keys?offset={offset}"
        elif limit is not None:
            url = f"keys?limit={limit}"
        else:
            url = "keys"
        response = await self._http_requests.get(url)

        return KeySearch(**response.json())

    async def get_key(self, key: str) -> Key:
        """Gets information about a specific API key.

        Args:

            key: The key for which to retrieve the information.

        Returns:

            The API key, or `None` if the key is not found.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     keys = await client.get_key("abc123")
        """
        response = await self._http_requests.get(f"keys/{key}")

        return Key(**response.json())

    async def update_key(self, key: KeyUpdate) -> Key:
        """Update an API key.

        Args:

            key: The information to use in updating the key. Note that if an expires_at value
                is included it should be in UTC time.

        Returns:

            The updated API key.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> from meilissearch_async_client.models.client import KeyUpdate
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     key_info = KeyUpdate(
                        key="abc123",
            >>>         indexes=["*"],
            >>>     )
            >>>     keys = await client.update_key(key_info)
        """
        # The json.loads(key.json()) is because Pydantic can't serialize a date in a Python dict,
        # but can when converting to a json string.
        if is_pydantic_2():
            payload = {  # type: ignore[attr-defined]
                k: v
                for k, v in json.loads(key.model_dump_json(by_alias=True)).items()
                if v is not None and k != "key"
            }
        else:  # pragma: no cover
            payload = {  # type: ignore[attr-defined]
                k: v
                for k, v in json.loads(key.json(by_alias=True)).items()
                if v is not None and k != "key"
            }
        response = await self._http_requests.patch(f"keys/{key.key}", payload)

        return Key(**response.json())

    async def multi_search(self, queries: list[SearchParams]) -> list[SearchResultsWithUID]:
        """Multi-index search.

        Args:

            queries: List of SearchParameters

        Returns:

            Results of the search

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> from meilisearch_python_async.models.search import SearchParams
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     queries = [
            >>>         SearchParams(index_uid="my_first_index", query"Some search"),
            >>>         SearchParams(index_uid="my_second_index", query="Another search")
            >>>     ]
            >>>     search_results = await client.search(queries)
        """
        url = "multi-search"
        if is_pydantic_2():
            response = await self._http_requests.post(
                url, body={"queries": [x.model_dump(by_alias=True) for x in queries]}  # type: ignore[attr-defined]
            )
        else:  # pragma: no cover
            response = await self._http_requests.post(
                url, body={"queries": [x.dict(by_alias=True) for x in queries]}  # type: ignore[attr-defined]
            )

        return [SearchResultsWithUID(**x) for x in response.json()["results"]]

    async def get_raw_index(self, uid: str) -> IndexInfo | None:
        """Gets the index and returns all the index information rather than an Index instance.

        Args:

            uid: The index's unique identifier.

        Returns:

            Index information rather than an Index instance.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.get_raw_index("movies")
        """
        response = await self.http_client.get(f"indexes/{uid}")

        if response.status_code == 404:
            return None

        return IndexInfo(**response.json())

    async def get_raw_indexes(
        self, *, offset: int | None = None, limit: int | None = None
    ) -> list[IndexInfo] | None:
        """Gets all the indexes.
        Args:

            offset: Number of indexes to skip. The default of None will use the Meilisearch
                default.
            limit: Number of indexes to return. The default of None will use the Meilisearch
                default.

        Returns all the index information rather than an Index instance.

        Returns:

            A list of the Index information rather than an Index instances.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.get_raw_indexes()
        """
        if offset is not None and limit is not None:
            url = f"indexes?offset={offset}&limit={limit}"
        elif offset is not None:
            url = f"indexes?offset={offset}"
        elif limit is not None:
            url = f"indexes?limit={limit}"
        else:
            url = "indexes"
        response = await self._http_requests.get(url)

        if not response.json()["results"]:
            return None

        return [IndexInfo(**x) for x in response.json()["results"]]

    async def get_version(self) -> Version:
        """Get the Meilisearch version.

        Returns:

            Information about the version of Meilisearch.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     version = await client.get_version()
        """
        response = await self._http_requests.get("version")

        return Version(**response.json())

    async def health(self) -> Health:
        """Get health of the Meilisearch server.

        Returns:

            The status of the Meilisearch server.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     health = await client.get_healths()
        """
        response = await self._http_requests.get("health")

        return Health(**response.json())

    async def swap_indexes(self, indexes: list[tuple[str, str]]) -> TaskInfo:
        """Swap two indexes.

        Args:

            indexes: A list of tuples, each tuple should contain the indexes to swap.

        Returns:

            The details of the task.

        Raises:

            MeilisearchCommunicationError: If there was an error communicating with the server.
            MeilisearchApiError: If the Meilisearch API returned an error.

        Examples:

            >>> from meilisearch_python_async import Client
            >>> async with Client("http://localhost.com", "masterKey") as client:
            >>>     index = await client.swap_indexes([("index_a", "index_b")])
        """
        processed_indexes = [{"indexes": x} for x in indexes]
        response = await self._http_requests.post("swap-indexes", processed_indexes)

        return TaskInfo(**response.json())
