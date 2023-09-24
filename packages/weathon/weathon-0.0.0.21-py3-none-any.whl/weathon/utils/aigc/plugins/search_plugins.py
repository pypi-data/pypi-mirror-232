import json
import requests
from semantic_kernel import SKContext
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from bs4 import BeautifulSoup
from weathon.crawler.utils.header import bing_header


class Search:

    def scrape_text(url, proxies) -> str:
        """Scrape text from a webpage

        Args:
            url (str): The URL to scrape text from

        Returns:
            str: The scraped text
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Content-Type': 'text/plain',
        }
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if response.encoding == "ISO-8859-1": response.encoding = response.apparent_encoding
        except:
            return "无法连接到该网页"
        soup = BeautifulSoup(response.text, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text

    @sk_function(name="bing_search", description="Bing Search Interface")
    @sk_function_context_parameter(name="query", description="query text")
    def bing_search(self, context:SKContext):
        query = context["query"]
        url = f"https://cn.bing.com/search?q={query}"
        response = requests.get(url, headers=bing_header)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        for g in soup.find_all('li', class_='b_algo'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                if not link.startswith('http'):
                    continue
                title = g.find('h2').text
                item = {'title': title, 'link': link}
                results.append(item)
        for r in results:
            print(r['link'])
        return results


