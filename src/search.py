from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
import requests
import re

from textwrap import shorten
from argparse import ArgumentParser

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

def gettext(elem):
	return elem.text.strip().replace("\n", "  ")

class Result:
	def __init__(self, title, desc, url):
		self.title = gettext(title)
		self.desc = gettext(desc)
		self.url = gettext(url)

	def format(self, width=80, url_only=False):
		if url_only:
			return self.url

		desc = shorten(self.desc, width)
		return f"{self.title}\n  {desc}\n  {self.url}\n"

def parse_results(html):
	soup = BeautifulSoup(html, 'html.parser')

	titles = soup.find_all('a', class_="result-link")
	descs = soup.find_all('td', class_="result-snippet")
	urls = soup.find_all('span', class_="link-text")

	results = [Result(*params) for params in zip(titles, descs, urls)]
	return results

def build_query(text, site):
	if site:
		search_text = f"site:{site} {text}"
	else:
		search_text = text
	safe_text = quote(search_text)
	query = f"{safe_text}&kl=&df="
	return query


def fetch_results(text, site=None):
	query = build_query(text, site)
	url = SEARCH_URL.format(query=query)
	
	headers = dict(HEADERS)
	headers['Content-Length'] = str(len(query))
	
	html = requests.get(url, headers=HEADERS).text
	return parse_results(html)


def main():
	parser = ArgumentParser()
	parser.add_argument('-n', type=int,
		help="Maximum number of results to return")
	parser.add_argument('-u', '--url-only', dest="url_only", action="store_true",
		help="Return only the urls of the results")
	parser.add_argument('-s', '--site',
		help="Restrict results to the domain <site>")
	parser.add_argument("query",
		help="The query to search")
	
	args = parser.parse_args()

	results = fetch_results(args.query, args.site)
	
	for result in results[:args.n]:
		print(result.format(url_only=args.url_only))

if __name__ == "__main__":
	main()
