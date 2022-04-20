import requests as rq
from bs4 import BeautifulSoup as bs
import sys
import pymongo
import datetime
import re
from multiprocessing import Process


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
    Function to build a list of dictionnary usable with PyMongo API
    The datetime is for sort purpose in Mongo
"""
def build_list(links):
    list_articles = []
    for link in links:
        list_articles.append({"Title": link.text.strip(), "URL": link["href"], "Date": datetime.datetime.utcnow()})
    return list_articles


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


""" 
    Function to persist data in MongoDB
    Don't stop in the case of duplicate ; new articles for the current website are inserted and we need to follow up with next website
"""
def mongo_insert(collection_mongo, data_list):
    try:
        collection_mongo.insert_many(data_list)
    except pymongo.errors.DuplicateKeyError :
        pass
    except pymongo.errors.PyMongoError as err:
        sys.exit(err)


"""
    Function to extract data from korben.info
"""
def korben():
    target_url = "https://korben.info/"
    response = send_request(target_url)

    """ Create a BeautifulSoup object to parse HTML response """
    html_soup = bs(response.content, "lxml")

    """ 
        Use BS API find_all() instead of CSS selector which is horrible in performance
        /!\ This selection exclude advertising post ; it returns link tags
    """ 
    links = html_soup.find_all("a", href=re.compile("https://korben.info/"), attrs={"itemprop": "url", "title": ""})
    articles = build_list(links)

    """ 
        Connect to and persist the data in MongoDB
        Connection is established in each Process as PyMongo isn't fork safe (see https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe)
    """
    mongo_connection = mongo_connect()
    mongo_insert(mongo_connection, articles)


"""
    Function to extract data from zdnet.fr
"""
def zdnet():
    target_url = "https://www.zdnet.fr/"
    response = send_request(target_url)

    """ Create a BeautifulSoup object to parse HTML response """
    html_soup = bs(response.content, "lxml")

    """ 
        I didn't find a way to use find_all without making tweaks after the first selection (duplicate links, ...)
        CSS selector is not as fast but the code remain simpler this way
    """ 
    links = html_soup.select("h3 > a")
    articles = build_list(links)

    """ 
        Connect to and persist the data in MongoDB
        Connection is established in each Process as PyMongo isn't fork safe (see https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe)
    """
    mongo_connection = mongo_connect()
    mongo_insert(mongo_connection, articles)


"""
    Main program 
    The requests to the different websites and the functions doesn't need to be sequential
    From my test using Process is faster than Thread by 10%, probably because of GI lock
    See https://luminousmen.com/post/asynchronous-programming-python3.5 for a great documentation on asynchronous programing in Python
"""
if __name__ == '__main__':
    """ List of websites I use as tech watch """
    websites = [korben, zdnet]

    """ Build the process list, then start them all before waiting for their end """
    processes = []
    for website in websites:
        processes.append(Process(target=website))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    """ End program gracefully """
    sys.exit(0)