

class FuelMagazine:
    def __init__(self):
        self.name = ""
        self.fuel_tank = 100
        self.fuel_per_ship = 2

    def fill_up_ship(self, ship):
        self.fuel_tank -= self.fuel_per_ship
        ship.fuel = 20

    def refill_tank(self):
        self.fuel_tank = 100

