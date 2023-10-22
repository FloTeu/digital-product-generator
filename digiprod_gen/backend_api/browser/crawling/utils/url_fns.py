
from digiprod_gen.backend_api.models.mba import MBAMarketplaceDomain



def get_main_url(marketplace: MBAMarketplaceDomain):
    return f"https://www.amazon.{marketplace}/s"

def get_hidden_keywordys(marketplace):
    if marketplace == MBAMarketplaceDomain.COM:
        return "Solid colors: 100% Cotton; Heather Grey: 90% Cotton, 10% Polyester; All Other Heathers: 50% Cotton, 50% Polyester Lightweight, Classic fit, Double-needle sleeve and bottom hem -Sweatshirt"
    elif marketplace == MBAMarketplaceDomain.UK:
        return "Solid colors: 100% Cotton; Heather Grey: 90% Cotton, 10% Polyester; All Other Heathers: 50% Cotton, 50% Polyester Lightweight, Classic fit, Double-needle sleeve and bottom hem -Sweatshirt"
    elif marketplace == MBAMarketplaceDomain.DE:
        return "Unifarben: 100% Baumwolle; Grau meliert: 90% Baumwolle -Langarmshirt"
    elif marketplace == MBAMarketplaceDomain.FR:
        return "Couleurs unies: 100% Coton; Gris chiné: 90% Coton, 10% Polyester; Autres couleurs chinées: 50% Coton, 50% Polyester"
    elif marketplace == MBAMarketplaceDomain.ES:
        return "Leggera, taglio classico, maniche con doppia cucitura e orlo inferiore +Maglietta -lunghe -Raglan -Canotta"
    elif marketplace == MBAMarketplaceDomain.IT:
        return "Color solido: 100% Algodon; Gris: 90% Algodon, 10% Poliester; otros colores: 50% Algodon, 50% Poliester"
    elif marketplace == MBAMarketplaceDomain.JP:
        return "Tシャツ 素材構成: 杢グレー: 綿80%, ポリエステル20% その他のカラー: 綿100%"
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
    elif marketplace == MBAMarketplaceDomain.JP:
        return "352484011"
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
    elif marketplace == MBAMarketplaceDomain.FR:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == MBAMarketplaceDomain.IT:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == MBAMarketplaceDomain.ES:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == MBAMarketplaceDomain.JP:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'rh': 'n:352484011', 'bbn': get_bbn(marketplace),
                  'hidden-keywords': get_hidden_keywordys(marketplace), 'qid': '160021'}
    else:
        raise NotImplementedError
            
    return params

