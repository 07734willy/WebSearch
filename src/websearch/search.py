from urllib.parse import quote
from bs4 import BeautifulSoup
from textwrap import shorten
import requests


SEARCH_URL = "https://duckduckgo.com/lite/?q={query}"

HEADERS = {
	 "Host": "lite.duckduckgo.com",
	 "User-Agent": "Mozilla/5.0 Firefox/78.0",
	 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	 "Accept-Language": "en-US,en;q=0.5",
	 "Referer": "https://lite.duckduckgo.com/",
	 "Content-Type": "application/x-www-form-urlencoded",
	 "Origin": "https://lite.duckduckgo.com",
	 "DNT": "1",
}


def cleantext(text):
	return text.strip().replace("\n", "  ")

class Result:
	def __init__(self, title, desc, url):
		self.title = cleantext(title)
		self.desc = cleantext(desc)
		self.url = cleantext(url)

	def format(self, width=80, url_only=False):
		if url_only:
			return self.url

		desc = shorten(self.desc, width)
		return f"{self.title}\n  {desc}\n  {self.url}\n"


def parse_results(html):
	soup = BeautifulSoup(html, 'html.parser')

	titles = soup.find_all('a', class_="result-link")
	descs = soup.find_all('td', class_="result-snippet")

	results = []
	for title, desc in zip(titles, descs):
		results.append(Result(
			title.text,
			desc.text,
			title['href'],
		))
	return results


def build_query(text, site):
	if site:
		search_text = f"site:{site} {text}"
	else:
		search_text = text
	safe_text = quote(search_text)
	query = f"{safe_text}&kl=&df="
	return query


def search(text, site=None):
	query = build_query(text, site)
	url = SEARCH_URL.format(query=query)
	
	headers = dict(HEADERS)
	headers['Content-Length'] = str(len(query))
	
	html = requests.get(url, headers=HEADERS).text
	return parse_results(html)
