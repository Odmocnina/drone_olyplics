from djitellopy import Tello

class Drone_controller:
    tello: Tello

    def __init__(self):
        self.tello = Tello()
        self.tello.connect()

        print(f"Battery: {self.tello.get_battery()}%")



    def fly(self, height):
        self.tello.takeoff()
        self.tello.move_up(height)

    def turn(self, direction, angle):
        if direction == "left":
            self.tello.rotate_clockwise(angle)
        elif direction == "right":
            self.tello.rotate_counter_clockwise(angle)

    def turn_right(self):
        self.turn("right", 90)

    def turn_left(self):
        self.turn("left", 90)