from djitellopy import Tello, TelloException
import time
import qr_reader

# Konstanty
MAX_STEPS = 100
STEP_LENGTH = 20  # cm
QR_LAND = {"pristat"}
QR_LEFT = {"vlevo"}
QR_RIGHT = {"vpravo"}

# Funkce pro reakci na nacteny QR kod
# param:
# tello - instance dronu
# text - nacteny text z QR kodu
# return:
# True pokud ma dron pristat, jinak False
def react_to_qr(tello: Tello, text: str) -> bool:
    msg = text.strip().lower() # ocisti text a hod na maly pismena
    if msg in QR_LAND:
        print("[QR] Přistávám podle QR:", msg)
        land(tello)
        return True
    elif msg in QR_LEFT:
        print("[QR] Otočka vlevo podle QR:", msg)
        turn_left(tello)
    elif msg in QR_RIGHT:
        print("[QR] Otočka vpravo podle QR:", msg)
        turn_right(tello)
    else:
        print("[QR] Neznámý příkaz v QR:", msg)
    return False

# Hlavni smycka pro let dronu
# param:
# tello - instance dronu
# frame_reader - instance pro cteni snimku z kamery dronu
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

        data = qr_reader.img_to_np_array(frame) # prevedeni na np pole
        data = qr_reader.read(data) # precteni qrkodu

        if data is not None:
            landing = react_to_qr(tello, data)
            if landing:
                running = False

# Funkce pro start, let a pripadne pristani dronu
# param:
# height - vyska v cm
# tello - instance dronu
def fly(height, tello):
    try: # pravdepodobne jste se o vyjkach neucili, ale jendoduse, try-catch je ze kod v try bloku se pokusi porvest
         # a pokud se neco pokazi, tak to vlze do except bloku, kde POKUD SE VZJIMKA SCHODUJE, tak se provede kod v
         # except bloku
        tello.takeoff()
        time.sleep(3)
        tello.move_up(height)
    except TelloException as e: # jaka vyjimka se muze chytit je definovano zde. TrelloException je vzjimka y dronu,
                                # pokud se neco pokazi s dronem tak to vleye do tutoho bloku, pokud by se stala jinaci
                                # , treba deleni nulou, chyba tak to sem nevleze
        print("TelloException:", e)
        try:
            tello.land()
        except Exception: # tutak se rekne jakakoliv vyjimka, uprime kdyby tady se vyjimka stala tak je to blby, protoze
                          # to nepristane
            pass # pass znamena igonruj vzjimku

        raise # tuto zase znamena vzhozeni vyjimky znovu, priklad: pokusim se delit nulou je to odchyceno, pass rekne
              # jedeme dal, snad je to osetreno dal v kodu, raise rekne tu je to divny radeji to tom dam vedet

# Funkce pro otoceni dronu
# param:
# direction - smer otoceni "left" nebo "right"
# angle - uhel otoceni ve stupnich
# tello - instance dronu
def turn(direction, angle, tello):
    if direction == "left":
            tello.rotate_clockwise(angle)
    elif direction == "right":
        tello.rotate_counter_clockwise(angle)

# Funkce pro otoceni dronu o 90 stupnu vpravo
# param:
# tello - instance dronu
def turn_right(tello):
    turn("right", 90, tello)

# Funkce pro otoceni dronu o 90 stupnu vlevo
# param:
# tello - instance dronu
def turn_left(tello):
    turn("left", 90, tello)

# Funkce pro pristani dronu
# param:
# tello - instance dronu
def land(tello):
    tello.land()