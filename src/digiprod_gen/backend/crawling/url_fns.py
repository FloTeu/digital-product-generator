


def get_form_details(form):
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    action = form.attrs.get("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value = input_tag.attrs.get("value", "")
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


def get_main_url(marketplace):
    if marketplace == "com":
        return "https://www.amazon.com/s"
    elif marketplace == "co.uk":
        return "https://www.amazon.co.uk/s"
    else:
        return "https://www.amazon.de/s"


def get_hidden_keywordys(marketplace):
    if marketplace == "com":
        return "ORCA"
    elif marketplace == "uk":
        return "Solid colors: 100% Cotton; Heather Grey: 90% Cotton, 10% Polyester; All Other Heathers: Classic Fit -Sweatshirt"
    else:
        return 'Unifarben: 100% Baumwolle; Grau meliert: 90% Baumwolle -Langarmshirt'


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


def get_bbn(marketplace):
    if marketplace == "com":
        return "12035955011"
    elif marketplace == "uk":
        return "83450031"
    else:
        return "77028031"


def get_url_query_params(marketplace, keyword, sort):
    if marketplace == "com":
        params = {'i': 'fashion-novelty', 'k': keyword, 's': get_sort_statement(sort), 'rh': 'p_6:ATVPDKIKX0DER',
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    elif marketplace == "uk":
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'rh': 'p_76:419122031,p_6:A3JWKAKR8XB7XF', 'bbn': get_bbn(marketplace),
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    else:
        params = {'i': 'clothing', 'k': keyword, 's': get_sort_statement(sort),
                  'rh': 'p_76:419122031,p_6:A3JWKAKR8XB7XF', 'bbn': get_bbn(marketplace), 'dc': "",
                  'hidden-keywords': get_hidden_keywordys(marketplace)}
    return params

