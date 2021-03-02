from urllib.parse import quote
from bs4 import BeautifulSoup
from textwrap import shorten
import requests

from contextlib import suppress
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILENAME = os.path.join(SCRIPT_DIR, "search_cache.json")

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

	def to_json(self):
		return vars(self)

	@classmethod
	def from_json(self, data):
		return Result(**data)

class Search:
	def __init__(self, text, site):
		self.text = text.strip()
		self.site = site
		self.results = []
		
	def build_query(self):
		if self.site:
			search_text = f"site:{self.site} {self.text}"
		else:
			search_text = self.text
		safe_text = quote(search_text)
		query = f"{safe_text}&kl=&df="
		return query

	def search(self):
		query = self.build_query()
		url = SEARCH_URL.format(query=query)
		
		headers = dict(HEADERS)
		headers['Content-Length'] = str(len(query))
		
		html = requests.get(url, headers=HEADERS).text
		self.results = parse_results(html)

	def matches(self, text, site):
		return text.strip() == self.text and site == self.site

	@classmethod
	def load(cls):
		with suppress(FileNotFoundError):
			with open(CACHE_FILENAME, "r") as f:
				data = json.load(f)
				search = Search(data['text'], data['site'])
				search.results = [Result.from_json(r) for r in data['results']]
				return search

	def dump(self):
		with open(CACHE_FILENAME, "w") as f:
			data = {'text': self.text, 'site': self.site, 'results': [
				result.to_json() for result in self.results]}
			json.dump(data, f)

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

def search(text, site=None):
	last_search = Search.load()
	if last_search and last_search.matches(text, site):
		return last_search.results
	
	new_search = Search(text, site)
	new_search.search()
	new_search.dump()
	return new_search.results
