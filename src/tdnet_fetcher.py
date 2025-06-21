import pandas as pd
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import math

TDNET_BASE_URL = "https://www.release.tdnet.info/inbs/"
ITEMS_PER_PAGE = 100
FIRST_PAGE_TABLE_INDEX = 1
SUBSEQUENT_PAGE_TABLE_INDEX = 3

class TdnetFetcher:
    def _get_soup(self, url: str, parser: str = "html.parser") -> BeautifulSoup:
        """Fetches a URL and returns a BeautifulSoup object."""
        with urlopen(url) as response:
            return BeautifulSoup(response.read(), parser)

    def _get_total_disclosures(self, soup: BeautifulSoup) -> int:
        """Extracts the total number of disclosures from the initial page soup."""
        num_of_kaiji_div = soup.find("div", {"class": "kaijiSum"})
        if not num_of_kaiji_div:
            return 0
        match = re.search(r"全(\d+)件", num_of_kaiji_div.text)
        return int(match.group(1)) if match else 0

    def _parse_disclosure_table(self, table: BeautifulSoup, target_date_str: str) -> list:
        """Parses a single disclosure table and returns a list of dictionaries."""
        disclosures_data = []
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            disclosure = {
                "日付": target_date_str,
                "時刻": "",
                "コード": "",
                "会社名": "",
                "表題": "",
                "url": "",
                "XBRL": ""
            }
            for td in tds:
                if "class" in td.attrs and len(td.attrs["class"]) > 1:
                    td_class = td.attrs["class"][1]
                    if td_class == "kjTime":
                        disclosure["時刻"] = td.text
                    elif td_class == "kjCode":
                        disclosure["コード"] = td.text
                    elif td_class == "kjName":
                        disclosure["会社名"] = td.text
                    elif td_class == "kjTitle":
                        link = td.find("a")
                        if link:
                            disclosure["表題"] = link.text
                            disclosure["url"] = TDNET_BASE_URL + link.get("href")
                        else:
                            disclosure["表題"] = "空"
                            disclosure["url"] = None
                    elif td_class == "kjXbrl":
                        link = td.find("a")
                        disclosure["XBRL"] = TDNET_BASE_URL + link.get("href") if link else None
            disclosures_data.append(disclosure)
        return disclosures_data

    def fetch_tdnet_disclosures(self, target_date_str: str) -> pd.DataFrame:
        """
        指定された日付のTDnet適時開示情報を取得し、DataFrameとして返す。
        """
        first_page_url = f"{TDNET_BASE_URL}I_list_{'001'}_{target_date_str}.html"
        first_page_soup = self._get_soup(first_page_url)
        
        summary_table = first_page_soup.find_all("table")[FIRST_PAGE_TABLE_INDEX]
        total_disclosures = self._get_total_disclosures(summary_table)

        print(f"{total_disclosures}件")

        if total_disclosures == 0:
            return pd.DataFrame(columns=["日付", "時刻", "コード", "会社名", "表題", "url", "XBRL"])

        all_disclosures = []
        num_of_page = math.ceil(total_disclosures / ITEMS_PER_PAGE)

        for i in range(num_of_page):
            page_num_str = str(i + 1).zfill(3)
            page_url = f"{TDNET_BASE_URL}I_list_{page_num_str}_{target_date_str}.html"
            page_soup = self._get_soup(page_url, "lxml") # Use lxml as in original for subsequent pages

            try:
                data_table = page_soup.find_all("table")[SUBSEQUENT_PAGE_TABLE_INDEX]
                all_disclosures.extend(self._parse_disclosure_table(data_table, target_date_str))
            except IndexError:
                print(f"Warning: Could not find data table on page {i+1}. Skipping.")
                continue
            except Exception as e:
                print(f"Error parsing page {i+1}: {e}")
                continue

        df = pd.DataFrame(all_disclosures, columns=["日付", "時刻", "コード", "会社名", "表題", "url", "XBRL"])
        return df
