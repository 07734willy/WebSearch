from argparse import ArgumentParser
from search import search

def main():
	parser = ArgumentParser()
	parser.add_argument('-n', type=int, default=5,
		help="Maximum number of results to return")
	parser.add_argument('-u', '--url-only', dest="url_only", action="store_true",
		help="Return only the urls of the results")
	parser.add_argument('-s', '--site',
		help="Restrict results to the domain <site>")
	parser.add_argument("query",
		help="The query to search")
	
	args = parser.parse_args()

	results = search(args.query, args.site)
	
	for result in results[:args.n]:
		print(result.format(url_only=args.url_only))

if __name__ == "__main__":
	main()
