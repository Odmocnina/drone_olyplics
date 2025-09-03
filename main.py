import drone_controller
import time
from djitellopy import Tello, TelloException

if __name__ == "__main__":
    tello = Tello()
    try:
        tello.connect()
        print("Baterie: " + str(tello.get_battery()))
        drone_controller.fly(20, tello)
        print("Drone started")
        time.sleep(5)  # visení
        tello.land()
        print("Drone landed")
        #drone_controller.main_loop(tello)
    finally:
        try:
            tello.end()
        except Exception:
            pass