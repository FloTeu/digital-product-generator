import argparse
import sys
import urllib.parse as urlparse
from urllib.parse import urlencode

from digiprod_gen.backend.browser.crawling.utils import url_fns


def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('keyword', help='Keyword that you like to query in utils', type=str)
    parser.add_argument('marketplace', help='Shortcut of utils marketplace. I.e "com" or "de", "co.uk"', type=str)
    parser.add_argument('pod_product',
                        help='Name of Print on Demand product. I.e "shirt", "premium", "longsleeve", "sweatshirt", "hoodie", "popsocket", "kdp"',
                        type=str)
    parser.add_argument('sort',
                        help='What kind of sorting do you want?. I.e "best_seller", "price_up", "price_down", "cust_rating", "oldest", "newest"',
                        type=str)

    if len(argv) == 5:
        argv = argv[1:5]

    # get all arguments
    args = parser.parse_args(argv)
    keyword = args.keyword
    marketplace = args.marketplace
    pod_product = args.pod_product
    sort = args.sort

    url = url_fns.get_main_url(marketplace)

    # rh set articles to prime
    params = url_fns.get_url_query_params(marketplace, keyword, sort)

    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)


if __name__ == '__main__':
    main(sys.argv)

