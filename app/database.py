from pymongo import MongoClient

def connect_to_mongo(uri="mongodb+srv://auburyqx0215:Ww876973145@cluster0.0hv3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="job_scraper", collection_name="jobs"):
    client = MongoClient(uri)
    return client[db_name]

def save_to_mongo(db, collection_name, data):
    collection = db[collection_name]
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

def query_jobs(db, collection_name, query):
    collection = db[collection_name]
    return list(collection.find(query))