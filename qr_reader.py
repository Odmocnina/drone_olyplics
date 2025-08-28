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

    if bbox is not None and draw: # vzkreseleni qr kodu jestli chceme
        pts = bbox.astype(np.int32)  # převod na int
        cv2.polylines(img, [pts], isClosed=True, color=(255, 0, 0), thickness=2) # co tuto je

    if data: # vzprnteni precteneho obsahu qr kodu
        print(f"Decoded Data: {data}")

    if show: # zobrayeni snimku jestli chceme
        cv2.imshow(window_name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return data # vystup z funkce, vrati prectene data
