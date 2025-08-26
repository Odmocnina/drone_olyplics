from drone_controller import Drone_controller
from qr_reader import QR_reader

if __name__ == "__main__":
    picture = "data/left.png"
    qr_reader = QR_reader(picture)
    data = qr_reader.read()
    drone_controler = Drone_controller()
    drone_controler.fly(50)
    print("Drone started")