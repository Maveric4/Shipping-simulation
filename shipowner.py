from seaCan import SeaCan
from ship import Ship
from random import randint as rand


class Shipowner:
    def __init__(self, nbr_seaCans):
        self.capital = 1000
        self.ships = []
        self.nbr_seaCans = nbr_seaCans
        self.seaCans = []

    def schedule_seaCans(self, seaMap):
        seaCans_for_ship = []
        for seaCan_it in range(1, 1+self.nbr_seaCans):
            dest_port = seaMap.ports[rand(0, seaMap.nbr_ports - 1)]
            src_port = seaMap.ports[rand(0, seaMap.nbr_ports - 1)]
            seaCans_for_ship.append(SeaCan(dest_port, src_port))
            self.seaCans.append(SeaCan(dest_port, src_port))
        return seaCans_for_ship

    def buy_ship(self, ship_cost, sea_map):
        self.capital -= ship_cost
        capacity = rand(50, 1000)
        seaCans = self.schedule_seaCans(self)
        new_ship = Ship(name="ship" + str(sea_map.nbr_ships), capacity=capacity, shipowner=self, seaCans=seaCans)
        self.ships.append(new_ship)
        sea_map.ships.append(new_ship)
        sea_map.nbr_ships += 1

    def repair_ship(self, ship):
        if ship.is_at_destiny_port():
            ship.dest_port_queue[0].repair()
        else:
            ship.is_going_to_shipyard = True

    def fill_up_ship(self, ship):
        ship.fill_up()

    def destroy_ship(self, ship):
        if ship.is_at_destiny_port():
            ship.dest_port_queue[0].destroy_ship()
        else:
            ship.is_going_to_shipyard = True
