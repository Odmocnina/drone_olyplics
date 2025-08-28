import drone_controller
import time
from djitellopy import Tello, TelloException

if __name__ == "__main__":
    tello = Tello()
    try:
        drone_controller.fly(20, tello)
        time.sleep(3)
        tello.move_up(20)
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