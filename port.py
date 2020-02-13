from dock import Dock
from warehouse import Warehouse
from fuelMagazine import FuelMagazine
from seaCan import SeaCan
from random import randint as rand


class Port:
    def __init__(self, name):
        self.position = [0, 0]
        self.docks = []
        self.unloading_warehouse = Warehouse(name="Unloading warehouse")
        self.loading_warehouse = Warehouse(name="Loading warehouse")
        self.fuel_magazine = FuelMagazine()
        self.size = 30
        self.name = name

    def create_docks(self, nbr_docks):
        for i in range(0, nbr_docks):
            temp_dock = Dock("Dock{}".format(i))
            self.docks.append(temp_dock)

    def create_warehouses(self, seaMap, nbr_seaCans=10):
        for seaCan_it in range(0, nbr_seaCans):
            dest_port = seaMap.ports[rand(0, seaMap.nbr_ports - 1)]
            src_port = seaMap.ports[rand(0, seaMap.nbr_ports - 1)]
            self.loading_warehouse.seaCans.append(SeaCan(dest_port, src_port))

    def fill_up_ship(self, ship):
        self.fuel_magazine.fill_up_ship(ship)