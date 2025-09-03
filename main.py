import drone_controller
import time
from djitellopy import Tello, TelloException

if __name__ == "__main__":
    tello = Tello()
    tello.connect()
    tello.streamon()
    frame_reader = tello.get_frame_read()
    print("f[DRON] Baterie: {int(tello.get_battery())}")
    
    timeout = time.time() + 5  # max 5 sekund
    while frame_reader.frame is None and time.time() < timeout:
        time.sleep(0.1)

    if frame_reader.frame is None:
        print("Stream se nepodařilo spustit.")
    else:
        print("Stream běží.")
        
    height = 150
    take_off_height = 80
    
    if height <= take_off_height:
        print("f[DRON] Nevalidni vyska - vyska vzletu {int(height)} musi byt vyzsi nez vyska pri startu {int(take_off_height)}")
    else:

        tello.takeoff()
        tello.move_up(height - take_off_height)  # aby kamera lépe viděla

        drone_controller.interval_scan_loop(tello, frame_reader, step_cm=25.0, min_cov_pct=5.0)
        
        tello.streamoff()
        tello.end()
