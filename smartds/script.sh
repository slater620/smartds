#!/bin/bash

# Fonction pour lancer le simulateur DroneKit-SITL
start_dronekit_sitl() {
    sudo dronekit-sitl copter
}

# Fonction pour lancer le serveur MavProxy
start_mavproxy() {
    sudo mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551 --out 127.0.0.1:14552
}

# Lancement en parallèle du simulateur DroneKit-SITL et du serveur MavProxy
start_dronekit_sitl & start_mavproxy

# Attendre que les processus se terminent
wait
