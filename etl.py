import requests as rq
from bs4 import BeautifulSoup as bs
import sys
import pymongo
from codetiming import Timer
import datetime


""" 
    Function dedicated to send request to target URL ; return requests object
"""
def send_request(target):
    """ 
        Fill HTTP header so this programm can be identified as a scrapper and blocked easily (best practice)
        Then send the request to target server (see https://docs.python-requests.org/en/latest/api/#exceptions for errors handling)
        here the program exit with any error (HTTP code 4XX/5XX, bad request, network problem...)
    """
    custom_agent = {"user-agent": "mypyscrapper/0.0.1"}
    try:
        response = rq.get(target, headers=custom_agent, timeout=0.500)
        response.raise_for_status()
    except rq.exceptions.RequestException as err:
        sys.exit(err)
    return response


"""
    Function dedicated to extract the elements I'm seeking on the page ; return a list of dictionnary (title and link to blog post)
    Some elements contains extra spaces hence strip method
"""
def extract_elements(soup, selector):
    elements_soup = soup.select(selector)
    elements = []
    for element in elements_soup:
        elements.append({"Title": element.text.strip(), "URL": element["href"], "Date": datetime.datetime.utcnow()})
    return elements

"""
    Functon to initiate a MongoDB connection on localhost / default port
    /!\ This should be changed, see https://docs.mongodb.com/guides/server/auth/
    Returns the database and collection as an object
"""
def mongo_connect():
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=1000)

        """ Initiate database and collection objects """
        mypyscrapper = client.mypyscrapper
        blog_posts = mypyscrapper.blog_posts

        """ Check if the database for this project exists """
        dbnames = client.list_database_names()

        if "mypyscrapper" not in dbnames:
            """ Create the database and the collection with a unique index on blog post link and a text index on title (text base search) """
            mypyscrapper.blog_posts.create_index([("URL", pymongo.ASCENDING)], unique=True)
            mypyscrapper.blog_posts.create_index([("Title", pymongo.TEXT)])
    except pymongo.errors.PyMongoError as err:
        sys.exit(err)
    return blog_posts


""" Function to persist data in MongoDB """
def mongo_insert(collection_mongo, data_list):
    try:
        collection_mongo.insert_many(data_list)
    except pymongo.errors.PyMongoError as err:
        sys.exit(err)


""" 
    Main function
    @Timer is a decorator that display elpased time
    see https://realpython.com/python-timer/ for more informations on monitoring and decorators
"""
@Timer()
def etl():
    target_url = "https://korben.info/"
    response = send_request(target_url)

    """ Create a BeautifulSoup object to parse HTML response """
    html_soup = bs(response.content, "lxml")

    """ 
        Define CSS selector to get titles of blog post then extract them from html soup
        /!\ Theses selectors exclude advertising post ; it returns link tags
    """ 
    css_selector_titles = "article div.entry-wrapper header h2.font-bold a.transition-colors"
    titles = extract_elements(html_soup, css_selector_titles)

    """ 
        Persist the data in MongoDB
    """
    mongo_db = mongo_connect()
    mongo_insert(mongo_db, titles)

    """ End program gracefully """
    sys.exit(0)


etl()