import requests
import aiohttp
from logging import Logger
from requests import Session
from weathon.crawler.utils.header import searxng_header
from typing import List, Optional,Union,Any, Dict
from semantic_kernel.connectors.search_engine.connector import ConnectorBase
from semantic_kernel.utils.null_logger import NullLogger


class SearXNG(ConnectorBase):

    """
    A search engine connector that uses the Bing Search API to perform a web search
    """
    def __init__(self, search_host:str="https://search.omycloud.site",
                 logger: Optional[Logger] = None,
                 secure:bool=True,
                 headers:Optional[dict]=searxng_header,
                 engines: Optional[List[str]] = [],
                 categories: Optional[List[str]] = [],
                 session:Optional[Session] = None,
                 aiosession: Optional[Any] = None,
                 return_format:str="json"
                 ) -> None:

        self.search_host = search_host
        self._logger = logger if logger else NullLogger()
        self.secure = secure
        self.headers = headers
        self.engines = engines
        self.categories = categories
        self.aiosession = aiosession
        self.session = session
        self.return_format = return_format


    def _search_api(self, datas:Dict={}) -> List[str]:
        if self.session:
            response = self.session.post(self.search_host, data=datas,headers=self.headers,verify=self.secure)
        else:
            response = requests.post(self.search_host, data=datas,headers=self.headers,verify=self.secure)

        if not response.ok:
            raise ValueError("Searx API returned an error: ", response.json())
        return response.json()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.search(*args, **kwds)

    
    def search(self, query:str, num_results: Union[str, int]=None, offset: str=None) -> List[str]:
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
            f"Received request for searxng web search with \
                        params:\nquery: {query}\nnum_results: {num_results}\noffset: {offset}"
        )
        self._logger.info(f"Sending Post request to {self.search_host}")

        # prepare post datas
        datas = {
            "q":query,
            "format":self.return_format,
        }
        if isinstance(self.engines, list) and len(self.engines) > 0:
            datas["engines"] = ",".join(self.engines)
        
        if isinstance(self.categories, list) and len(self.categories) > 0:
            datas["categories"] = ",".join(self.categories)
        
        result = self._search_api(datas=datas)
        return result["results"][:num_results]
    

    async def _search_api_async(self, datas:Dict={}) -> List[str]:
        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.search_host, headers=self.headers,data=datas) as response:
                    if not response.ok:
                        raise ValueError("Searx API returned an error: ", response.json())
                    result = await response.json()
        else:
            async with self.aiosession.post(self.search_host, headers=self.headers,data=datas,verify=self.secure) as response:
                if not response.ok:
                    raise ValueError("Searx API returned an error: ", response.json())
                result = await response.json()
        return result
    
    async def search_async(self, query: str, num_results:  Union[str, int]=1, offset: Union[str, int]=0) -> List[str]:
        """
        Returns the search results of the query provided by pinging the searxng search API.
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
            f"Received request for searxng web search with \
                        params:\nquery: {query}\nnum_results: {num_results}\noffset: {offset}"
        )
        self._logger.info(f"Sending Post request to {self.search_host}")

        # prepare post datas
        datas = {
            "q":query,
            "format":self.return_format,
        }
        if isinstance(self.engines, list) and len(self.engines) > 0:
            datas["engines"] = ",".join(self.engines)
        
        if isinstance(self.categories, list) and len(self.categories) > 0:
            datas["categories"] = ",".join(self.categories)
        
        result = await self._search_api_async(datas=datas)
        return result["results"][:num_results]