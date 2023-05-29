
from digiprod_gen.backend.data_classes.mba import MBAMarketplaceDomain



def get_main_url(marketplace: MBAMarketplaceDomain):
    if marketplace == MBAMarketplaceDomain.COM:
        return "https://www.amazon.com/s"
    elif marketplace == MBAMarketplaceDomain.UK:
        return "https://www.amazon.co.uk/s"
    elif marketplace == MBAMarketplaceDomain.DE:
        return "https://www.amazon.de/s"
    else:
        raise NotImplementedError


def get_hidden_keywordys(marketplace):
    if marketplace == MBAMarketplaceDomain.COM:
        return "Solid colors: 100% Cotton; Heather Grey: 90% Cotton, 10% Polyester; All Other Heathers: Classic Fit -Sweatshirt"
    elif marketplace == MBAMarketplaceDomain.UK:
        return "Solid colors: 100% Cotton; Heather Grey: 90% Cotton, 10% Polyester; All Other Heathers: Classic Fit -Sweatshirt"
    elif marketplace == MBAMarketplaceDomain.DE:
        return "Unifarben: 100% Baumwolle; Grau meliert: 90% Baumwolle -Langarmshirt"
    else:
        raise NotImplementedError


def get_sort_statement(sort):
    "best_seller", "price_up", "price_down", "cust_rating", "oldest", "newest"
    if sort == "best_seller":
        return ""
    elif sort == "price_up":
        return "price-asc-rank"
    elif sort == "price_down":
        return "price-desc-rank"
    elif sort == "cust_rating":
        return "review-rank"
    elif sort == "oldest":
        return "-daterank"
    elif sort == "newest":
        return "date-desc-rank"
    else:
        raise ("sort statement is not known!")


def get_bbn(marketplace: MBAMarketplaceDomain):
    if marketplace == MBAMarketplaceDomain.COM:
        return "12035955011"
    elif marketplace == MBAMarketplaceDomain.UK:
        return "83450031"
    elif marketplace == MBAMarketplaceDomain.DE:
        return "77028031"
    else:
        raise NotImplementedError


def get_url_query_params(marketplace, keyword, sort):
    if marketplace == MBAMarketplaceDomain.COM:
        params = {'i': 'fashion-novelty', 'k': keyword, 's': get_sort_statement(sort), 'rh': 'p_6:ATVPDKIKX0DER',
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == MBAMarketplaceDomain.UK:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'rh': 'p_76:419122031,p_6:A3JWKAKR8XB7XF', 'bbn': get_bbn(marketplace),
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == MBAMarketplaceDomain.DE:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'rh': 'p_76:419122031,p_6:A3JWKAKR8XB7XF', 'bbn': get_bbn(marketplace), 'dc': "",
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    else:
        raise NotImplementedError
            
    return params

