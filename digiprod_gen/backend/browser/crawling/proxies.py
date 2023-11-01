import random
from typing import Optional, List
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain


PERFECT_PRIVACY_PROXIES = [
    {"url": "strasbourg.perfect-privacy.com", "name": "Strasbourg", "location": "France", "working": True},
    {"url": "paris.perfect-privacy.com", "name": "Paris", "location": "France", "working": True},
    {"url": "calais.perfect-privacy.com", "name": "Calais", "location": "France", "working": True},
    {"url": "london1.perfect-privacy.com", "name": "London", "location": "United Kingdom", "working": True},
    {"url": "london2.perfect-privacy.com", "name": "London", "location": "United Kingdom", "working": True},
    {"url": "prague.perfect-privacy.com", "name": "Prague", "location": "Czech Republic", "working": True},
    {"url": "riga.perfect-privacy.com", "name": "Riga", "location": "Latvia", "working": True},
    {"url": "oslo.perfect-privacy.com", "name": "Oslo", "location": "Norway", "working": True},
    {"url": "reykjavik.perfect-privacy.com", "name": "Reykjavik", "location": "Iceland", "working": True},
    {"url": "amsterdam1.perfect-privacy.com", "name": "Amsterdam", "location": "Niederlande", "working": True},
    {"url": "amsterdam2.perfect-privacy.com", "name": "Amsterdam", "location": "Niederlande", "working": True},
    {"url": "amsterdam3.perfect-privacy.com", "name": "Amsterdam", "location": "Niederlande", "working": True},
    {"url": "amsterdam4.perfect-privacy.com", "name": "Amsterdam", "location": "Niederlande", "working": True},
    {"url": "amsterdam5.perfect-privacy.com", "name": "Amsterdam", "location": "Niederlande", "working": True},
    {"url": "basel1.perfect-privacy.com", "name": "Basel", "location": "Schweiz", "working": True},
    {"url": "basel2.perfect-privacy.com", "name": "Basel", "location": "Schweiz", "working": True},
    {"url": "belgrade.perfect-privacy.com", "name": "Belgrade", "location": "Serbien", "working": True},
    {"url": "berlin.perfect-privacy.com", "name": "Berlin", "location": "Deutschland", "working": True},
    {"url": "bucharest.perfect-privacy.com", "name": "Bucharest", "location": "Rum\u00e4nien", "working": True},
    {"url": "chicago.perfect-privacy.com", "name": "Chicago", "location": "USA", "working": False},
    {"url": "copenhagen.perfect-privacy.com", "name": "Copenhagen", "location": "D\u00e4nemark", "working": True},
    {"url": "dallas.perfect-privacy.com", "name": "Dallas", "location": "USA", "working": True},
    {"url": "erfurt.perfect-privacy.com", "name": "Erfurt", "location": "Deutschland", "working": True},
    {"url": "frankfurt1.perfect-privacy.com", "name": "Frankfurt", "location": "Deutschland", "working": True},
    {"url": "frankfurt2.perfect-privacy.com", "name": "Frankfurt", "location": "Deutschland", "working": True},
    {"url": "hamburg.perfect-privacy.com", "name": "Hamburg", "location": "Deutschland", "working": True},
    {"url": "hongkong.perfect-privacy.com", "name": "Hongkong", "location": "China", "working": True},
    {"url": "istanbul.perfect-privacy.com", "name": "Istanbul", "location": "T\u00fcrkei", "working": True},
    {"url": "losangeles.perfect-privacy.com", "name": "Los Angeles", "location": "USA", "working": False},
    {"url": "madrid.perfect-privacy.com", "name": "Madrid", "location": "Spanien", "working": True},
    {"url": "malmoe.perfect-privacy.com", "name": "Malmoe", "location": "Schweden", "working": True},
    {"url": "manchester.perfect-privacy.com", "name": "Manchester", "location": "Gro\u00dfbritannien",
     "working": True},
    {"url": "melbourne.perfect-privacy.com", "name": "Melbourne", "location": "Australien", "working": True},
    {"url": "miami.perfect-privacy.com", "name": "Miami", "location": "USA", "working": True},
    {"url": "milan.perfect-privacy.com", "name": "Milan", "location": "Italien", "working": True},
    {"url": "montreal.perfect-privacy.com", "name": "Montreal", "location": "Kanada", "working": True},
    {"url": "moscow1.perfect-privacy.com", "name": "Moscow", "location": "Russland", "working": True},
    {"url": "moscow2.perfect-privacy.com", "name": "Moscow", "location": "Russland", "working": True},
    {"url": "newyork.perfect-privacy.com", "name": "New York", "location": "USA", "working": True},
    {"url": "nuremberg1.perfect-privacy.com", "name": "Nuremberg", "location": "Deutschland", "working": True},
    {"url": "nuremberg2.perfect-privacy.com", "name": "Nuremberg", "location": "Deutschland", "working": True},
    {"url": "rotterdam1.perfect-privacy.com", "name": "Rotterdam", "location": "Niederlande", "working": True},
    {"url": "rotterdam2.perfect-privacy.com", "name": "Rotterdam", "location": "Niederlande", "working": True},
    {"url": "rotterdam3.perfect-privacy.com", "name": "Rotterdam", "location": "Niederlande", "working": True},
    {"url": "rotterdam4.perfect-privacy.com", "name": "Rotterdam", "location": "Niederlande", "working": True},
    {"url": "rotterdam5.perfect-privacy.com", "name": "Rotterdam", "location": "Niederlande", "working": True},
    {"url": "singapore1.perfect-privacy.com", "name": "Singapore", "location": "Singapur", "working": True},
    {"url": "singapore2.perfect-privacy.com", "name": "Singapore", "location": "Singapur", "working": True},
    {"url": "steinsel1.perfect-privacy.com", "name": "Steinsel", "location": "Luxemburg", "working": True},
    {"url": "steinsel2.perfect-privacy.com", "name": "Steinsel", "location": "Luxemburg", "working": True},
    {"url": "stockholm1.perfect-privacy.com", "name": "Stockholm", "location": "Schweden", "working": True},
    {"url": "stockholm2.perfect-privacy.com", "name": "Stockholm", "location": "Schweden", "working": True},
    {"url": "telaviv.perfect-privacy.com", "name": "TelAviv", "location": "Israel", "working": True},
    {"url": "tokyo.perfect-privacy.com", "name": "Tokyo", "location": "Japan", "working": True},
    {"url": "zurich1.perfect-privacy.com", "name": "Zurich", "location": "Schweiz", "working": True},
    {"url": "zurich2.perfect-privacy.com", "name": "Zurich", "location": "Schweiz", "working": True},
    {"url": "zurich3.perfect-privacy.com", "name": "Zurich", "location": "Schweiz", "working": True}
]

def get_private_http_proxy_list(user_name, password, marketplace: Optional[MBAMarketplaceDomain]=None, port=3128) -> List[str]:
    http_proxy_list = []
    for proxy in PERFECT_PRIVACY_PROXIES:
        url = f"http://{user_name}:{password}@{proxy['url']}:{port}"
        if marketplace == None:
            http_proxy_list.append(url)
        else:
            if marketplace == MBAMarketplaceDomain.COM and proxy["location"] in ["USA", "Iceland"]:
                http_proxy_list.append(url)
            elif marketplace in [MBAMarketplaceDomain.DE, MBAMarketplaceDomain.FR, MBAMarketplaceDomain.IT, MBAMarketplaceDomain.ES] and proxy["location"] in ["France", "Deutschland", "Norway", "Schweiz", "Rum\u00e4nien", "D\u00e4nemark", "Spanien", "Schweden", "Italien", "Niederlande", "Luxemburg"]:
                http_proxy_list.append(url)
            elif marketplace in [MBAMarketplaceDomain.UK] and proxy["location"] in ["United Kingdom", "Gro\u00dfbritannien"]:
                http_proxy_list.append(url)
            elif marketplace in [MBAMarketplaceDomain.JP] and proxy["location"] in ["Japan"]:
                http_proxy_list.append(url)
    return http_proxy_list

def get_random_private_proxy(user_name, password, marketplace: Optional[MBAMarketplaceDomain]=None, port=3128) -> str:
    private_http_proxy_list = get_private_http_proxy_list(user_name, password, marketplace=marketplace, port=port)
    return random.choice(private_http_proxy_list)