import aiohttp
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import Union, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnusbaseScraper:
    def __init__(self, auth: Union[Dict[str, str], str], mode: str = "normal"):
        self.auth = auth
        self.mode = mode
        self.timeout = 10

    async def search(self, term: str, value: str) -> Union[str, Dict[str, List[Dict[str, str]]]]:
        """
        Perform search on Snusbase with the given term and value.
        :param term: The search term.
        :param value: The value to search.
        :return: A dictionary containing the search results or an error message string.
        """
        url_map = {"normal": 'https://snusbase.com/search', "beta": 'https://beta.snusbase.com'}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}

        if self.mode not in url_map:
            return "Invalid mode"

        try:
            async with aiohttp.ClientSession() as session:
                if self.mode == "normal":
                    return await self._normal_search(session, url_map[self.mode], headers, term, value)
                else:
                    return await self._beta_search(session, url_map[self.mode], headers, term, value)

        except (aiohttp.ClientError, aiohttp.InvalidURL, aiohttp.ClientResponseError) as e:
            logger.error(f'Client error: {str(e)}')
            return f'Error: {str(e)}'

        except asyncio.TimeoutError:
            logger.error('Timeout error')
            return "Timed out"

        except Exception as e:
            logger.error(f'An unexpected error occurred: {str(e)}')
            return f'An error occurred: {str(e)}'

    async def _normal_search(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str], term: str,
                             value: str) -> Union[str, Dict[str, List[Dict[str, str]]]]:
        """
        Perform normal search on Snusbase.
        :param session: The aiohttp ClientSession.
        :param url: The URL to perform the search.
        :param headers: The headers to be used in the request.
        :param term: The search term.
        :param value: The value to search.
        :return: A dictionary containing the search results or an error message string.
        """
        try:
            async with session.get(url, headers=headers, cookies=self.auth, timeout=self.timeout) as csrf_response:
                csrf_response.raise_for_status()
                csrf_soup = BeautifulSoup(await csrf_response.text(), 'html.parser')
                input_tag = csrf_soup.find('input', {'name': 'csrf_token'})
                csrf_token = input_tag['value']

            data = {'csrf_token': csrf_token, 'term': value, 'searchtype': term}
            async with session.post(url, headers=headers, cookies=self.auth, data=data, timeout=self.timeout) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return self._extract_data_normal(soup)

        except Exception as e:
            logger.error(f'Error during normal search: {str(e)}')
            return f'Error: {str(e)}'

    async def _beta_search(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str], term: str,
                           value: str) -> Union[str, Dict[str, List[Dict[str, str]]]]:
        """
        Perform beta search on Snusbase.
        :param session: The aiohttp ClientSession.
        :param url: The URL to perform the search.
        :param headers: The headers to be used in the request.
        :param term: The search term.
        :param value: The value to search.
        :return: A dictionary containing the search results or an error message string.
        """
        try:
            data = {'term': value, 'activation_code': self.auth, 'type': term}
            async with session.post(url, headers=headers, data=data, timeout=self.timeout) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return self._extract_data_beta(soup)

        except Exception as e:
            logger.error(f'Error during beta search: {str(e)}')
            return f'Error: {str(e)}'

    def _extract_data_normal(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract data from the normal search response.
        :param soup: The BeautifulSoup object containing the response.
        :return: A dictionary containing the extracted data.
        """
        results = {}
        searchtools_divs = soup.find_all('div', class_='searchtools')
        tables = soup.find_all('table')

        for div, table in zip(searchtools_divs, tables):
            top_bar_div = div.find('div', id='topBar')
            database_name = top_bar_div.get_text(strip=True).replace("View Full", "").strip()
            results[database_name] = []

            tbody = table.find('tbody')
            rows = tbody.find_all('tr')

            for row in rows:
                key_column, value_column = row.find_all('td')
                key = key_column.get_text(strip=True)
                value = value_column.get_text(strip=True)
                results[database_name].append({key: value})

        return results

    def _extract_data_beta(self, soup: BeautifulSoup) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract data from the beta search response.
        :param soup: The BeautifulSoup object containing the response.
        :return: A dictionary containing the extracted data.
        """
        results = {}
        try:
            sb_results = soup.find('div', id='sb_results')
            results_divs = sb_results.find_all('div', class_='results')

            for result_div in results_divs:
                label_element = result_div.find('label', class_='r-t')
                database_name = label_element.find('span').text.strip()
                results[database_name] = []

                r_i_divs = result_div.find_all('div', class_='r-i')

                for r_i_div in r_i_divs:
                    data_entries = {}
                    spans = r_i_div.find_all('span')

                    if len(spans) % 2 == 0:
                        for i in range(0, len(spans), 2):
                            key = spans[i].get_text(strip=True)
                            value = spans[i + 1].get_text(strip=True)
                            data_entries[key] = value

                        results[database_name].append(data_entries)

            return results
        except Exception as e:
            logger.error(f'Error during data extraction in beta mode: {str(e)}')
            return {}
