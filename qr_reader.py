import cv2
import numpy as np

def read(self, img, draw=True, show=False, window_name="QR"):
    detector = cv2.QRCodeDetector()
    data, bbox, straight = detector.detectAndDecode(img)

    if bbox is not None and draw:
        pts = bbox.astype(np.int32)  # převod na int
        cv2.polylines(self.img, [pts], isClosed=True, color=(255, 0, 0), thickness=2)

    if data:
        print(f"Decoded Data: {data}")

    if show:
        cv2.imshow(window_name, self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return data
