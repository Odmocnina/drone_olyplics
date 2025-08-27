from djitellopy import Tello, TelloException
import time

MAX_STEPS = 100
STEP_LENGTH = 20  # cm
QR_LAND = {"pristat"}
QR_LEFT = {"vlevo"}
QR_RIGHT = {"vpravo"}

def react_to_qr(tello: Tello, text: str) -> bool:
    msg = text.strip().lower() # ocisti text a mrdi na maly pismena
    if msg in QR_LAND:
        print("[QR] Přistávám podle QR:", msg)
        tello.land()
        return True
    elif msg in QR_LEFT:
        print("[QR] Otočka vlevo podle QR:", msg)
        tello.rotate_counter_clockwise(90)
    elif msg in QR_RIGHT:
        print("[QR] Otočka vpravo podle QR:", msg)
        tello.rotate_clockwise(90)
    else:
        print("[QR] Neznámý příkaz v QR:", msg)
    return False

def main_loop(tello, frame_reader):
    steps = 0
    running = True
    while steps < MAX_STEPS and running:
        try:
            tello.move_forward(STEP_LENGTH)
            time.sleep(2)
            steps = steps + 1
        except TelloException as e:
            time.sleep(0.2)

        frame = frame_reader.frame
        if frame is None:
            continue

def fly(height, tello):
    try:
        tello.takeoff()
        time.sleep(3)
        tello.move_up(height)
    except TelloException as e:
        print("TelloException:", e)
        try:
            tello.land()
        except Exception:
            pass
        raise
    finally:
        try:
            tello.end()
        except Exception:
            pass

def turn(direction, angle, tello):
    if direction == "left":
            tello.rotate_clockwise(angle)
    elif direction == "right":
        tello.rotate_counter_clockwise(angle)

def turn_right(tello):
    turn("right", 90, tello)

def turn_left(tello):
    turn("left", 90, tello)

def land(tello):
    tello.land()