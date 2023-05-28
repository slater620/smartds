from dronekit import connect, VehicleMode,LocationGlobalRelative
import time
import argparse
import geopy.distance
import pymongo


class Drone:

    def __init__(self,url , database_name ,collection_name):
        self.vehicle = None
        self.uid= "1234"
        self.database_name= database_name
        self.collection = collection_name
        self.url = url
        self.document = None
        self.destination = None


    def determine_destination(self,collection_station):
        """
        Trouve le point le plus proche d'un point cible dans une liste de points
        """
        min_distance = float('inf')  # Initialisation à une distance infinie
        to_cur =(self.vehicle.location.global_relative_frame.lat,self.vehicle.location.global_relative_frame.lon)

        client = pymongo.MongoClient(self.url)

        db = client[self.database_name]

        # Sélection de la collection
        collection = db[collection_station]

        # Récupération de tous les documents de la collection
        stations = collection.find()


        for station in stations:
            to_cord = ( station['latitude'], station['longitude'] )
            d = self.get_dstance(to_cord, to_cur)
            if d < min_distance:
                min_distance = d
                self.destination = station

        print(self.destination)
    

    
    def connect_to_database(self):

        client = pymongo.MongoClient(self.url)

        db = client[self.database_name]

        collection = db[self.collection]

         # Recherche du document avec le champ spécifié
        self.document = collection.find_one({"uid": self.uid})

        if self.document:

            print("le drone a été trouvé.")

        else:
            print("Aucun drone correspondant n'a été trouvé.")

    
    def update(self):

        client = pymongo.MongoClient(self.url)

        db = client[self.database_name]

        collection = db[self.collection]

        collection.update_one({"uid": self.uid}, {'$set': self.document})



    #connect to drone
    def connectMyCopter(self):
        parser =  argparse.ArgumentParser(description='commands')
        parser.add_argument('--connect')
        args = parser.parse_args()

        connection_string = args.connect
        baud_rate = 57600
        print("\nConnecting to vehicle on: %s" % connection_string)
        self.vehicle = connect(connection_string,baud=baud_rate,wait_ready=True)
        print("\nConnection sucessful")



    #arm and takeoff to meteres
    def arm_and_takeoff(self):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print("Basic pre-arm checks")
        
        # Don't let the user try to arm until autopilot is ready
        while not  self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

            
        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        while not  self.vehicle.armed:      
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(3) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
          

            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt) 

            if  self.vehicle.location.global_relative_frame.alt>=3*0.95: #Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(1)



    def land(self):

        """
        Land the vehicle
        """

        # Check if vehicle can be armed and is not already in LAND mode
        if self.vehicle.armed and self.vehicle.mode.name != 'LAND':
            # Change vehicle mode to LAND
            self.vehicle.mode = VehicleMode('LAND')
            # Wait for vehicle to land and disarm
            while self.vehicle.armed:
                print('Vehicle is landing...')
                time.sleep(1)
            print('Vehicle has landed and disarmed.')
        else:
            print('Vehicle cannot be landed.')
        


    def get_dstance(self , cord1, cord2):
        #return distance n meter
        return (geopy.distance.geodesic(cord1, cord2).km)*1000



    def goto_location(self,to_lat, to_long ):    
            
        print(" Global Location (relative altitude): %s" % self.vehicle.location.global_relative_frame)
        curr_lat = self.vehicle.location.global_relative_frame.lat
        curr_lon = self.vehicle.location.global_relative_frame.lon
        curr_alt = self.vehicle.location.global_relative_frame.alt

        # set to locaton (lat, lon, alt)
        to_lat = to_lat
        to_lon = to_long
        to_alt = curr_alt

        to_pont = LocationGlobalRelative(to_lat,to_lon,to_alt)
        self.vehicle.simple_goto(to_pont, airspeed=15)
        
        to_cord = (to_lat, to_lon)

        while True:
            
            self.document['latitude'] = self.vehicle.location.global_relative_frame.lat
            self.document['longitude'] = self.vehicle.location.global_relative_frame.lon
            # Mettre à jour le document dans la collection
            self.update()
            curr_lat = self.vehicle.location.global_relative_frame.lat
            curr_lon = self.vehicle.location.global_relative_frame.lon
            curr_cord = (curr_lat, curr_lon)
            print("curr location: {}".format(curr_cord))
            distance = self.get_dstance(curr_cord, to_cord)
            print("distance ramaining {}".format(distance))
            if distance <= 2:
                print("Reached within 2 meters of target location...")
                break
            time.sleep(1)



