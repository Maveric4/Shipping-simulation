from fuelMagazine import FuelMagazine
from dock import Dock
from ship import Ship
from random import randint as rand


class Shipyard:
    def __init__(self, name):
        self.position = [0, 0]
        self.fuel_magazine = FuelMagazine()
        self.docks = []
        self.position = [0, 0]
        self.name = name
        self.size = 70

    def create_docks(self, nbr_docks):
        for i in range(0, nbr_docks):
            temp_dock = Dock("Dock{}".format(i))
            self.docks.append(temp_dock)

    def repair(self, ship):
        ship.is_being_repaired = True
        for dock in self.docks:
            if not dock.docked_ship:
                dock.is_empty = False
                dock.docked_ship = ship
                break

    def has_empty_slots(self):
        it = 0
        for dock in self.docks:
            if dock.docked_ship:
                it += 1
        return not it == len(self.docks)

    def is_still_being_repaired(self, ship):
        dock = next((dock for dock in self.docks if dock.docked_ship == ship), None)
        if "port" in ship.src_port_queue[0].name:
            print(ship.src_port_queue[0].name)
        if dock.next_repair_step(ship):
            return True
        else:
            dock.docked_ship = None
            return False

    def fill_up_ship(self, ship):
        self.fuel_magazine.fill_up_ship(ship)

    def make_new_ship(self, seaMap):
        capacity = rand(50, 1000)
        index = rand(0, self.nbr_shipowners - 1)
        shipowner = self.shipowners[index]
        seaCans = shipowner.schedule_seaCans(self)
        new_ship = Ship(name="ship"+str(seaMap.nbr_ships), capacity=capacity, shipowner=shipowner, seaCans=seaCans)
        seaMap.find_place(new_ship)
        seaMap.ships.append(new_ship)
        return new_ship

    def destroy_ship(self, seaMap, ship):
        seaMap.ships.remove(ship)
        seaMap.nbr_ships -= 1
        ship.shipowner.capital += 100

