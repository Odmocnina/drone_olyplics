import cv2
import numpy as np

# Funkce pro prevod snimku na numpy array
# param:
# frame - snimek (obrazek)
# return:
# gray - snimek prevedeny na numpy array (sedy)
def img_to_np_array(frame):
    img = frame.copy() # kopie snimku, lebo to prej muze byt nejak pokurveny jinacima vlaknama
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # frame na np pole, aby to read funkce spapala
    return gray

# Funkce pro cteni QR kodu ye snimku co bzl naskenovan
# param:
# img - snimek (numpy array)
# draw - vykreslit ohraniceni QR kodu do snimku
# show - zobrazit snimek v okne
# window_name - nazev okna
# return:
# data - prectena data z QR kodu nebo None
def read(img, draw=True, show=False, window_name="QR"):
    detector = cv2.QRCodeDetector() # magie s cv2 knivnou, co mi neni rovno po tom je mi hovno
    data, bbox, straight = detector.detectAndDecode(img)

    if bbox is not None and draw: # vykreseleni qr kodu jestli chceme
        pts = bbox.astype(np.int32)  # prevod na int
        cv2.polylines(img, [pts], isClosed=True, color=(255, 0, 0), thickness=2) # co tuto je

    if data: # vzprnteni precteneho obsahu qr kodu
        print(f"[QR] Decoded Data: {data}")

    if show: # zobrazeni snimku jestli chceme
        cv2.imshow(window_name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return data # vystup z funkce, vrati prectene data

# Funkce pro detekci QR kodu a jeho pozice ve snimku
# param:
# frame - snimek (obrazek)
# return:
# data - prectena data z QR kodu nebo None
# center - stred QR kodu jako (x, y) nebo None
# coverage - procentualni pokryti QR kodu ve snimku jako float
# pts - body ohraniceni QR kodu jako numpy array nebo None
def detect_qr_pose(frame):
    if frame is None:
        return None, None, 0.0, None

    if len(frame.shape) == 3: # kontrola jestli je frame barevny
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # prevod na sedy
    else:
        gray = frame

    detector = cv2.QRCodeDetector() # inicializace detektoru
    data, bbox, _ = detector.detectAndDecode(gray) # detekce a dekodovani QR kodu

    if bbox is None:
        return None, None, 0.0, None

    pts = bbox.reshape(-1, 2).astype(np.float32) # body ohraniceni QR kodu
    cx, cy = pts.mean(axis=0) # stred QR kodu
    area_qr = cv2.contourArea(pts) # plocha QR kodu
    h, w = gray.shape[:2] # w je sirka, h je vyska
    coverage = (area_qr / float(w * h)) * 100.0 if w > 0 and h > 0 else 0.0 # jestli vyska a sirka neni 0, tak
    # vzpocitane procento pokryti, jinak 0

    return (data if data != "" else None), (float(cx), float(cy)), float(coverage), pts # vraceni hodnot

# Funkce pro ziskani procentualniho pokryti QR kodu ve snimku
# param:
# frame - snimek (obrazek)
# return:
# coverage - procentualni pokryti QR kodu ve snimku jako float
def qr_coverage_percent(frame) -> float:
    data, _, cov, _ = detect_qr_pose(frame)
    return cov
