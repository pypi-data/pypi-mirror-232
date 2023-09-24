import urllib
import requests
from urllib.parse import urlparse
from typing import List, Optional
from semantic_kernel.connectors.search_engine import BingConnector


class Bing(BingConnector):
    def search(self, query: str, num_results: Union[str, int], offset: str) -> List[str]:
        """

        Args:
            query: search query
            num_results: the number of search results to return
            offset: the number of search results to ignore

        Returns:
            list of search results
        """

        if not query:
            raise ValueError("query cannot be 'None' or empty.")

        if not num_results:
            num_results = 1
        if not offset:
            offset = 0

        num_results = int(num_results)
        offset = int(offset)

        if num_results <= 0:
            raise ValueError("num_results value must be greater than 0.")
        if num_results >= 50:
            raise ValueError("num_results value must be less than 50.")

        if offset < 0:
            raise ValueError("offset must be greater than 0.")

        self._logger.info(
            f"Received request for bing web search with \
                        params:\nquery: {query}\nnum_results: {num_results}\noffset: {offset}"
        )

        _base_url = "https://api.bing.microsoft.com/v7.0/search"
        _request_url = f"{_base_url}?q={urllib.parse.quote_plus(query)}&count={num_results}&offset={offset}"

        self._logger.info(f"Sending GET request to {_request_url}")

        headers = {"Ocp-Apim-Subscription-Key": self._api_key}

        with requests.Session() as session:
            response = session.get(_request_url, headers=headers)
            if response.status == 200:
                data = response.json()
                pages = data["webPages"]["value"]
                self._logger.info(pages)
                result = list(map(lambda x: x["snippet"], pages))
                self._logger.info(result)
                return result
            else:
                return []

