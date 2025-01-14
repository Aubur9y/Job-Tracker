import os

def load_config():
    return {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb+srv://auburyqx0215:Ww876973145@cluster0.0hv3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"),
        "HEADLESS": False,
    }