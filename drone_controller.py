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
            move_forward(tello, STEP_LENGTH)
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
        time.sleep(6)
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
        tello.rotate_counter_clockwise(angle)
    elif direction == "right":
        tello.rotate_clockwise(angle)

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
    
def move_forward(tello, length):
    try:
        tello.move_forward(length)
        print(f"Dron se posunul dopředu o {length} cm.")
    except Exception as e:
        print(f"Chyba při posunu dopředu: {e}")
        
def move_back(tello, length):
    try:
        tello.move_back(length)
        print(f"Dron se posunul dozadu o {length} cm.")
    except Exception as e:
        print(f"Chyba při posunu dozadu: {e}")
        
# Funkce: let dopředu a pokus o načtení QR před dronem
# param:
#   tello - instance dronu Tello
#   frame_reader - objekt z tello.get_frame_read(), poskytuje aktuální snímek v .frame
#   length_cm - vzdálenost v cm, o kterou má dron popoletět dopředu
#   scan_timeout_s - kolik sekund po doletu zkoušet detekovat QR
#   sleep_step_s - pauza mezi čtením frame (šetrnější k CPU)
# return:
#   True  -> pokud se během čtení QR provedl příkaz, který misi ukončil (např. přistání)
#   False -> pokud QR nebyl nalezen / neukončil misi
def forward_and_scan_qr(tello: Tello, frame_reader, length_cm: int, scan_timeout_s: float = 6.0, sleep_step_s: float = 0.05) -> bool:
    try:
        tello.move_forward(int(length_cm))
        print(f"[Mise] Letím vpřed o {int(length_cm)} cm, pak hledám QR…")
    except Exception as e:
        print(f"[Mise] Chyba při letu vpřed: {e}")
        # když se nepodaří popoletět, i tak zkus krátce číst QR (třeba už nějaký je před námi)

    deadline = time.time() + float(scan_timeout_s)
    ended = False

    while time.time() < deadline:
        print("Zkousim cist qr")
        frame = getattr(frame_reader, "frame", None)
        if frame is None:
            print("Cteni bylo neuspesne")
            time.sleep(sleep_step_s)
            continue

        # převedeme na numpy (šedotón) a zkusíme přečíst QR
        gray = qr_reader.img_to_np_array(frame)
        data = qr_reader.read(gray, draw=False, show=False)

        if data:
            print(f"[QR] Nalezen QR obsah: {data}")
            # zareaguj na QR – pokud přistál, ukonči
            if react_to_qr(tello, data):
                ended = True
                break
            if data == "VPRAVO":
                move_forward(tello, 200)
            # krátká pauza po akci (např. otočka), ať se stabilizuje
            time.sleep(1.0)

        time.sleep(sleep_step_s)

    return ended
