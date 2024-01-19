import random
from typing import Dict, List

import streamlit as st
from digiprod_gen.backend.agent.tools.common import tool

from digiprod_gen.backend.agent.models.api import CrawlingMBARequest, CrawlMBAProductsDetailRequest
from digiprod_gen.backend.api.common import CONFIG
from digiprod_gen.backend.browser.crawling.utils.utils_mba import get_random_headers
from digiprod_gen.backend.models.mba import MBAMarketplaceDomain, MBAProductCategory, MBAProduct
from digiprod_gen.backend.etl.transform_fns import request2mba_overview_url
from digiprod_gen.backend.agent.memory import global_memory_container
from digiprod_gen.backend.agent.models.memory import MemoryId, MemoryAddResponse
from digiprod_gen.frontend.backend_caller import BackendCaller

SESSION_ID: str = "AiAgent"

@tool("crawlOverviewMBATool", args_schema=CrawlingMBARequest, required_memory_ids=[], adds_memory_ids=[MemoryId.MBA_PRODUCTS])
def crawl_overview_mba(search_term: str,
                       marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM,
                       product_category: MBAProductCategory = MBAProductCategory.SHIRT
                       ) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba and receive mba products"""
    #Crawls mba overview page and returns a list of MBAProduct

    proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
        st.secrets.proxy_perfect_privacy.user_name,
        st.secrets.proxy_perfect_privacy.password)
    postcode = CONFIG.mba.get_marketplace_config(marketplace).postcode
    headers = get_random_headers(marketplace)
    crawling_request: CrawlingMBARequest = CrawlingMBARequest(search_term=search_term,
                                                            marketplace=marketplace,
                                                            product_category=product_category,
                                                            mba_overview_url=None,
                                                            headers=headers,
                                                            proxy=proxy,
                                                            postcode=postcode)

    crawling_request.mba_overview_url = request2mba_overview_url(crawling_request)
    backend_caller = BackendCaller(CONFIG.backend)
    try:
        response = backend_caller.post(f"/browser/crawling/mba_overview?session_id={SESSION_ID}",
                                                 json=crawling_request.dict())
    except Exception as e:
        raise e
    if response.status_code != 200:
        raise ValueError("Status code != 200")
    global_memory_container[MemoryId.MBA_PRODUCTS] = [MBAProduct(**product_dict)
                                                      for product_dict in response.json()]


@tool("randomSearchTerm", required_memory_ids=[], adds_memory_ids=[MemoryId.SEARCH_TERM])
def get_random_search_term(
            ) -> Dict[str, str]:
    """use to get search term"""
    niches = """100 Days of School, 2nd Amendment / Second Amendment, 3D Animator, 3D Printing, 911 Dispatcher, Accountant, Action Figure, ADHD Awareness, Administrative assistant, Adult Humor, Aerobics, Aeronautical Engineering, Aerospace Engineering, Aesthetician, Afro, Agriculture, Air Traffic Controller, Aircraft Mechanic, Airline Pilot, Alchemy, Ambulance Driver, American Civil War reenactment, American History, Amputee, Animal Rescue, Anime, Anthropology, Anti Abortion, Anti Vaccine, Antiquing, Aquaponics, Aquarium, Arborist, Arcade Gaming, Archeologist, Archery, Architect, Arm Wrestling, Arrowhead Hunting, Art Teacher, Artificial Intelligence, Astronomy, Astrophysics, Atheist, Athletic Director, Athletic Trainer, ATV Quad Riding, Audiology, Aunt, Aunt to be, Author, Autism, Auto Body Painter, Auto Detailing, Auto Mechanic, Autocross, Aviation, Avocado, Axe Throwing, Axolotl, Babysitter, Bachelor Party, Bacon, Baking, Ball Games, Ballet, Balloon modelling, Banker, Barber, Barista, Bartender, Baton Twirling, BBQ, BDSM, Beach Sports, Beach Wrestling, Beachcombing, Beard, Beatboxing, Beautician, Beekeeping, Beer Pong, Behavior Analyst, Behavior Therapist, Behaviour therapy, Bible, Biblical, Bicycling, Big Brother, Big Sister, Bigfoot, Billiards, Bingo Cards Game, Biochemistry, Biology, Biomedical Engineering, Bird Photography, Bird Watching, Birds, Birthday, Blacksmith, Blogging, Blood Donor, Boardgames, Boating, Boba Tea, Bodybuilding, Bonsai Tree, Boomerang, Botany, Bowling, Boyfriend, Braille, Bridal Party, Bride, Bride and Groom, Bride to be, Bridesmaid, Bubble Tea, Bug Collecting, Bullfighting, Bus Driver, Butcher, Cabinetry, Cafeteria Worker, Calligraphy, Camping, Cancer, Canoeing, Car Mechanic, Car Racing, Car Restoration, Car Salesman, Cardistry, Caregiver, Carpenter, Cartoon, Casino, Cats, Cattle Show, Ceiling Tile Installer, Cellular Biology, Cerebral Palsy, Chain Saw, Chakra Healing, Charcoal drawing, Cheerleading, Cheese, Chef, Chemical Engineer, Chemistry, Chess, Chicken, Childcare Provider, Chinchilla, Chiropractor / Chiropractic, Chocolate, Choreographer, Church, Cigar, Circus, Civil Engineering, Civil War, Classic Cars, Claw Machine, Climate Change, Climbing, CNC Machinist, Coding, Coffee, Coin Collector / Numismatics, Combine / Combine Harvester Racing, Comic Books, Compost, Computers, Condiment, Conspiracy Theory, Construction, Construction Birthday, Cornhole, Correctional Officer, Cosmetology, Cosmology, Cosplay, Country Girl, Cousin, Cow, Cowboy, Cowgirl, Crab, Craft Beer, Crane Operator, Crawfish, Crayons, Criminal Investigation, Crocheting, Crop Duster, Cross Country Running, Cross Stitch, Cruising, Crunchy Mom, Cryptocurrency, Cryptozoology, Curling, Custodian, Dad, Dad to be, Dairy Free, Dancing, Darts, Data Analyst, Data Science, Database Administration, Daycare Teacher, Deadlifting, Deaf Awareness, Debate, Decaf, Demolition Derby, Dentist, Dermatology, Dessert, Diabetes, Dialysis, Diesel Engine, Diesel Mechanic, Diesel Truck, Digital Marketer, Dim Sum, Dinosaurs, Dirt Bike, Dirt Track Racing, Disco, Divorce, Dj / Disc jockey, Dog, Dog Agility, Dog Grooming, Dog Rescue / rescue dog, Dog Sitting, Dog Training, Donuts, Dorodango, Drag Queen, Drag Racing, Drifting, Drinking, Drone Flying, Drywall, Ducks, Dumpster Diving, Earth Science, Earthquake, Echocardiography, Ecology, Economics, Electric bicycle / e bike, Electrical Engineering, Electrician, Elementary School, Elevator Mechanic, Embroidery, Embryo Transfer Day, Employee Appreciation, EMTs and paramedics, Encaustic painting, English Civil War Reenactment, English Literature, Entomology, Environment, Environmentalist, Epilepsy Awareness, Equestrian, Essential Oil, Esthetician, Event Planning, Eyelash / Lash Artist, Fabricator, Family Vacation, Farming, Fashion Designing, Fast Food, Feminism, Fiance, Fiancee, Figure Skating, Film History, Filmmaker, Firefighter, First responder, Fishing, Fitness, Flat Earth, Flea Market, Flight Attendant, Florist, Folkrace, Food Truck, Forensic Science, Forestry, Forex Trading, Fossil Collection, Freemason / Masonry (fraternity), Frog, Fruits, Fundraising, Funeral Director, Furry Fandom / Fursuiting, Gambling, Game Shows, Gaming, Gangsta Rap, Garbage Truck, Gardening, Gastroenterology, Gemology, Gender Equality, Gender Reveal, Gender Roles, Genealogy, Genetic counselor, Geocaching, Geography, Geology, Geophysics, Geriatrics, Ghost Hunting, Girlfriend, Girls Trip, GIS (Geographic Information System), Glassblowing, Global Warming, Gluten Free, Go Kart Racing, Goats, Godfather, Godmother, Goldsmith, Graduation, Graffiti, Grammar, Grandma, Grandpa, Graphic Designing, Great Grandma, Great Grandpa, Groom, Groom to be, Groomsmen, Guinea Pig, Gun Control, Gym, Gymnastics, Hairdresser, Hairstylist, Ham Radio, Hamster, Handyman, Heart Attack Survivor, Heart Surgery, Hebrew, Helicopter, Help Desk, Herpetology, High School, Hiking, Hip Replacement, History, Hitchhiking, HO Scale Model Train, Hoe (Heavy equipment operator), Holidays & Celebrations, Home brewing, Homeowner, Homeschool, Horse, Horticulture, Hot Dog, Hot Rods, HR / Human Resources, Hula Hoop, Hunting, Husband, HVAC, Hydroponics, Hysterectomy, Ice Cream Truck, Ice Skating, Illuminate, Immersive Railroading, Information Technology, Insurance, Interior Design, Introvert, IVF, Janitor, Javascript, JDM, Jesus, Jet Ski, Junk Food, K9 Police, Kayaking, Keto Diet, Kidney, Knee Replacement, Knitting, Koi Fish, Kpop, Lab technician, Lampworking, Land Surveyor, Landscaping, Language Learning, Language Pathology (Speech Language Pathology), Lapidary, Laser Engraving, Law School, Lawn Mowing, Lawyer, LDS Mormon Missionary, Lemonade Stand, LGBTQ, Librarian, Lifeguard, Lifted Truck, Lineman (football), Linux, Little Brother, Little Sister, Livestock, Loan Officer, Loteria, Lucid dreaming, Lumberjack, Machine Learning, Machinist, Magician, Magnet Fishing, Makeup Artist, Marathon, Marching Band, Marine Biology, Marketing, Marriage and Family Therapy, Martial Arts, Massage Therapist, Masters Degree, Math, Mechanical Engineering, Medical Assistant, Medical"""

    search_term = random.choices(niches.split(","))[0].strip()
    global_memory_container[MemoryId.SEARCH_TERM] = search_term
    return search_term



@tool("crawlProductsMBATool", required_memory_ids=[MemoryId.SELECTED_MBA_PRODUCTS], adds_memory_ids=[MemoryId.SELECTED_MBA_PRODUCTS])
def crawl_products_detail_mba(
            marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM
            ) -> Dict[str, List[MBAProduct]]:
    """use to crawl amazon mba product detail pages and receive list of enriched mba products"""
    mba_products = global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS]
    def crawl_product_mba(mba_product: MBAProduct,
                          marketplace: MBAMarketplaceDomain = MBAMarketplaceDomain.COM
                          ) -> MBAProduct:
        """use to crawl amazon mba and receive enriched mba product"""
        proxy = CONFIG.mba.get_marketplace_config(marketplace).get_proxy_with_secrets(
            st.secrets.proxy_perfect_privacy.user_name,
            st.secrets.proxy_perfect_privacy.password)
        backend_caller = BackendCaller(CONFIG.backend)
        response = backend_caller.post(f"/browser/crawling/mba_product?session_id={SESSION_ID}&proxy={proxy}",
                                       json=mba_product.dict())
        if response.status_code != 200:
            raise ValueError(response.json())
        return MBAProduct(**response.json())

    final_mba_products = []
    for mba_product in mba_products:
        final_mba_products.append(crawl_product_mba(mba_product, marketplace))

    global_memory_container[MemoryId.SELECTED_MBA_PRODUCTS] = final_mba_products
    global_memory_container.status.detail_pages_crawled = True

    return [mba_prod.asin for mba_prod in final_mba_products]

