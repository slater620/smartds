from Drone.drone import*
from Mission.mission import*
from dotenv import load_dotenv
import os



# Charge les variables d'environnement à partir du fichier .env

load_dotenv()
url = os.getenv('URL')
database_name = os.getenv('DATABASE_NAME')
collection_drone = os.getenv('COLLECTION_DRONE')
collection_mission = os.getenv('COLLECTION_MISSION')
collection_station = os.getenv('COLLECTION_STATION')




drone = Drone(url , database_name , collection_drone)

drone.connectMyCopter()

while(True):

    print("==================================")

    drone.connect_to_database()


    if(drone.document):

        mission = MissionLivraison(drone,"ON", "livraison","livraison" ,url , database_name ,collection_mission)

        mission.connect_to_database()

        if(mission.document):
            
            drone.document['etat']=="ON"

            drone.update()
            
            #drone.collection.update_one({"uid": drone.uid, "etat":"ON"}, {'$set': drone.document})
            
            if(mission.document['etat']=="ON"):


                mission.my_mission()

                time.sleep(1)

                drone.determine_destination(collection_station)

                mission.document["etat"]="RETOUR"

                mission.update()


                mission.return_mission()

                time.sleep(1)

                mission.document["etat"]="OFF"

                mission.update()

                #mission.collection.update_one({"uid": drone.uid, "etat":"ON"}, {'$set': mission.document})

            else :
                print("Aucune mission correspondant n'a été trouvé.")

    else:
        print("Aucun drone correspondant n'a été trouvé.")

    time.sleep(1)






