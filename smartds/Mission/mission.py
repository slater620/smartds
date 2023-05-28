from dronekit import VehicleMode
import time
import pymongo


class Mission():
    
    def __init__(self , drone,etat,type, goal ,url , database_name ,collection_name) :
        self.drone = drone
        self.type = type
        self.etat = etat
        self.goal = goal
        self.document = None
        self.url = url
        self.database_name = database_name
        self.collection = collection_name

    
    def connect_to_database(self):

        client = pymongo.MongoClient(self.url)

        db = client[self.database_name]

        collection = db[self.collection]

         # Recherche du document avec le champ spécifié
        self.document = collection.find_one({"uid": self.drone.uid , "etat":"ON"})

        if self.document:

            print("la mission a été trouvé.")

        else:
            print("Aucune mission correspondant n'a été trouvé.")

    

    def my_mission(self):
        pass


    def update(self):

        client = pymongo.MongoClient(self.url)

        db = client[self.database_name]

        collection = db[self.collection]

        collection.update_one({"uid": self.drone.uid, "etat":"ON"}, {'$set': self.document})



class MissionLivraison(Mission):


    def my_mission(self):

        print("=========================================================================================================")

        self.drone.arm_and_takeoff()
        self.drone.goto_location(self.document['latitude'], self.document['longitude'])
        print("Destination complete")
        time.sleep(2)
        self.drone.land()
        time.sleep(1)
        print("Atterissage")
        time.sleep(2)
        print("Returning to Launch")
        self.drone.vehicle.mode = VehicleMode("RTL")

        print("=========================================================================================================")


    def return_mission(self):
        
        print("=========================================================================================================")
        self.drone.arm_and_takeoff()
        self.drone.goto_location( self.drone.destination['latitude'] , self.drone.destination['longitude'])
        print("Retour")
        time.sleep(2)
        self.drone.land()
        time.sleep(1)
        print("Atterissage")
        time.sleep(2)
        print("Returning to Launch")
        self.drone.vehicle.mode = VehicleMode("RTL")

        print("=========================================================================================================")