import drone_controller
import time
from djitellopy import Tello, TelloException

if __name__ == "__main__":
    tello = Tello()
    tello.connect()
    tello.streamon()
    frame_reader = tello.get_frame_read()

    tello.takeoff()
    tello.move_up(60)  # aby kamera lépe viděla

    # Popoletí vpřed 200 cm a ~6s se snaží načíst QR
    ukonceno = drone_controller.forward_and_scan_qr(tello, frame_reader, length_cm=180, scan_timeout_s=6.0)

    if not ukonceno:
        # QR nic “konečného” neudělal (např. nepřistál) → udělej, co chceš dál
        tello.land()
    tello.streamoff()
    tello.end()
