from pymongo import MongoClient

def connect_to_mongo(uri="mongodb+srv://auburyqx0215:Ww876973145@cluster0.0hv3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="job_scraper", collection_name="jobs"):
    client = MongoClient(uri)
    return client[db_name]

def save_to_mongo(db, collection_name, data):
    """
    Save data to MongoDB with deduplication logic.
    
    If a document with the same job_title, company_name, and location exists,
    it will be updated with the new data. Otherwise, the document will be inserted.

    Returns:
        int: The number of new records inserted into the database.
    """
    collection = db[collection_name]
    new_records_count = 0

    if isinstance(data, list):  # Handle bulk insertion
        for record in data:
            try:
                result = collection.update_one(
                    {
                        "job_title": record.get("job_title"),
                        "company_name": record.get("company_name"),
                        "location": record.get("location"),
                    },
                    {"$set": record},  # Update the document if it exists
                    upsert=True,  # Insert if the document doesn't exist
                )
                # Count as new record if an insert occurred
                if result.upserted_id:
                    new_records_count += 1
            except Exception as e:
                print(f"Error saving record to MongoDB: {e}")
    else:  # Handle single insertion
        try:
            result = collection.update_one(
                {
                    "job_title": data.get("job_title"),
                    "company_name": data.get("company_name"),
                    "location": data.get("location"),
                },
                {"$set": data},  # Update the document if it exists
                upsert=True,  # Insert if the document doesn't exist
            )
            # Count as new record if an insert occurred
            if result.upserted_id:
                new_records_count += 1
        except Exception as e:
            print(f"Error saving record to MongoDB: {e}")

    return new_records_count

def query_jobs(db, collection_name, query):
    collection = db[collection_name]
    return list(collection.find(query))