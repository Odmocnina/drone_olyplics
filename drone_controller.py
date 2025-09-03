from djitellopy import Tello, TelloException
import time
import qr_reader

# Konstanty
MAX_STEPS = 100
STEP_LENGTH = 20  # cm
QR_LAND = {"přistát"}
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
        return "land"
    elif msg in QR_LEFT:
        print("[QR] Otočka vlevo podle QR:", msg)
        turn_left(tello)
        return "left"
    elif msg in QR_RIGHT:
        print("[QR] Otočka vpravo podle QR:", msg)
        turn_right(tello)
        return "right"
    else:
        print("[QR] Neznámý příkaz v QR:", msg)
    return None

# Hlavni smycka pro let dronu
# param:
# tello - instance dronu
# frame_reader - instance pro cteni snimku z kamery dronu
def main_loop_steps(tello, frame_reader):
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
                
def main_loop(tello, frame_reader):
    length_of_gap = 170
    running = True
    time_for_scanning_qr_code = 6.0
    sleep_step_s = 0.05

    last_cmd = None
    last_seen_time = 0.0
    cooldown_s = 1.5  # ignoruj stejný QR po 1.5 s

    while running:
        try:
            move_forward(tello, length_of_gap)

            deadline = time.time() + time_for_scanning_qr_code
            while time.time() < deadline:
                print("Zkousim cist qr")
                frame = getattr(frame_reader, "frame", None)
                if frame is None:
                    time.sleep(sleep_step_s)
                    continue

                data_np = qr_reader.img_to_np_array(frame)
                data = qr_reader.read(data_np, draw=False, show=False)  # draw vypnuto

                if not data: # odfiltrovani praznych retezcu
                    time.sleep(sleep_step_s)
                    continue

                cmd = data.strip().lower()
                # kdyz tam tuto neni tak to pak provede ten prikaz y qr 2 krat
                if last_cmd == cmd and (time.time() - last_seen_time) < cooldown_s:
                    time.sleep(sleep_step_s)
                    continue

                reaction = react_to_qr(tello, data)
                if reaction:
                    if reaction == "land":
                        running = False
                    break # tohle panu Hladkému neukazujte

                last_cmd = cmd
                last_seen_time = time.time()

                time.sleep(sleep_step_s)
        except TelloException:
            time.sleep(0.2)

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
    
def center_on_qr(tello, frame_reader,
                 timeout_s=10.0,
                 deadband_px=30,         # tolerance středu v pixelech
                 k_yaw_deg_per_px=0.05,  # převod pixel -> stupně yaw
                 k_vert_cm_per_px=0.05   # převod pixel -> cm nahoru/dolů
                 ):
    """Pokusí se vycentrovat QR do středu obrazu. Vrací True/False podle úspěchu."""
    t_end = time.time() + timeout_s
    while time.time() < t_end:
        frame = getattr(frame_reader, "frame", None)
        if frame is None:
            time.sleep(0.05); continue

        data, center, _, _ = qr_reader.detect_qr_pose(frame)
        if center is None:  # QR není ve frame
            time.sleep(0.05); continue

        h, w = frame.shape[:2]
        cx, cy = center
        ex = cx - (w / 2.0)   # + vpravo
        ey = cy - (h / 2.0)   # + dolů

        did = False
        # yaw
        if abs(ex) > deadband_px:
            yaw = int(max(5, min(25, abs(ex) * k_yaw_deg_per_px)))
            tello.rotate_clockwise(yaw if ex > 0 else -yaw)
            did = True
        # výška
        if abs(ey) > deadband_px:
            dz = int(max(20, min(40, abs(ey) * k_vert_cm_per_px)))
            if ey > 0: 
                tello.move_down(dz)
            else:      
                tello.move_up(dz)
            did = True

        if not did:
            return True  # jsme v toleranci
        time.sleep(0.3)   # stabilizace
    return False

def interval_scan_loop(tello, frame_reader,
                       step_cm=10,
                       min_cov_pct=30.0,
                       max_steps=200,
                       sleep_step_s=0.06,
                       post_action_cooldown_s=1.0,
                       min_height=60.0):
    last_cmd = None
    last_seen_time = 0.0
    cooldown_s = 1.5
    i = 0

    for _ in range(int(max_steps)):
        i = i + 1
        try:
            tello.move_forward(int(step_cm))
            print(f"[KROK] +{int(step_cm)} cm vpřed")
        except Exception as e:
            print(f"[KROK] Chyba letu: {e}")

        # krátká stabilizace obrazu po pohybu
        time.sleep(0.25)
        
        height = tello.get_height()
        print(f"[KROK] +{int(height)} cm v vzduchu")
        if height < min_height:
            print("[KROK] Moc nizko, pristavam")
            break

        # skenuj pár sekund, ale stačí i krátké okno, QR je blízko
        deadline = time.time() + 2.0
        while time.time() < deadline:
            frame = getattr(frame_reader, "frame", None)
            if frame is None:
                print("[Kamera] Snimek nebyl nacten")
                time.sleep(sleep_step_s); 
                continue

            data, center, cov, _ = qr_reader.detect_qr_pose(frame)
            # není QR -> pokračuj ve skenování (nebo nový krok po vypršení deadline)
            if center is None:
                print("[QR] Nebyl nalezen QR v snimku")
                time.sleep(sleep_step_s); 
                continue
                
            
            centered = center_on_qr(tello, frame_reader, timeout_s=2.5)
            if not centered:
                print("[QR] Nepodařilo se přesně vycentrovat (pokračuji).")
            else:
                print("[QR] Vycentrovano")

            print(f"[QR] coverage ~ {cov:.1f}%")
            if cov < float(min_cov_pct):
                # QR je ještě malý -> po deadline uděláme další krok vpřed
                time.sleep(sleep_step_s); 
                continue

            # přečti text a proveď
            gray = qr_reader.img_to_np_array(frame)
            txt = qr_reader.read(gray, draw=False, show=False)

            if not txt:
                # někdy decode selže i když bbox je; zkus další frame v okně
                time.sleep(sleep_step_s); 
                continue

            cmd = txt.strip().lower()
            # anti-double trigger
            if last_cmd == cmd and (time.time() - last_seen_time) < cooldown_s:
                time.sleep(sleep_step_s); 
                continue

            print(f"[QR] obsah: {cmd}")
            reaction = react_to_qr(tello, txt)
            last_cmd = cmd
            last_seen_time = time.time()

            if reaction == "land":
                print("[Mise] Přistáno podle QR – konec.")
                return

            # po provedení akce dej chvilku na stabilizaci a skoč na další krok
            time.sleep(post_action_cooldown_s)
            break  # ukonči vnitřní sken a pokračuj dalším krokem

    print("[Mise] Konec smyčky (max_steps vyčerpáno).")
