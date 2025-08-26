import cv2
import numpy as np

class QR_reader:
    def __init__(self, src):
        # src může být cesta (str) nebo už načtené pole (numpy array)
        if isinstance(src, str):
            img = cv2.imread(src)
            if img is None:
                raise FileNotFoundError(f"Nelze načíst obrázek: {src}")
        else:
            img = src
            if img is None:
                raise ValueError("Obrázek je None.")
        self.img = img

    def read(self, draw=True, show=False, window_name="QR"):
        detector = cv2.QRCodeDetector()
        data, bbox, straight = detector.detectAndDecode(self.img)

        # bbox: tvar typicky (4,1,2), dtype float32
        if bbox is not None and draw:
            pts = bbox.astype(np.int32)  # převod na int
            # polylines očekává list polygonů ve tvaru (N,1,2)
            cv2.polylines(self.img, [pts], isClosed=True, color=(255, 0, 0), thickness=2)

        if data:
            print(f"Decoded Data: {data}")

        if show:
            cv2.imshow(window_name, self.img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return data

    def read_multi(self, draw=True, show=False, window_name="QR_multi"):
        detector = cv2.QRCodeDetector()
        ok, decoded_info, points, straight_qrcodes = detector.detectAndDecodeMulti(self.img)

        results = []
        if ok and decoded_info:
            for txt, bbox in zip(decoded_info, points):
                results.append(txt)
                if draw and bbox is not None:
                    pts = bbox.astype(np.int32)  # (4,1,2)
                    cv2.polylines(self.img, [pts], True, (0, 255, 0), 2)

        if show:
            cv2.imshow(window_name, self.img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return results
