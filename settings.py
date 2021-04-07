from pymongo import MongoClient
class mongoDB:
    def __init__(self):
        try:
            uri = "mongodb://root:pass12345@localhost:27017/?authSource=admin"
            # mongo = MongoClient(host="localhost", port=27017, serverSelectionTimeoutMS = 1000)
            self.mongo = MongoClient(uri) #bismillahSpin
            self.db = self.mongo.bismillahSpin
        except Exception as e:
            print("Can't connect to DB , err:",e)
    
    def getDB(self):
        return self.db

    def getMongo(self):
        return self.mongo


initDB = mongoDB()
db = initDB.getDB()
mongo = initDB.getMongo()