import numpy as np
from random import randint as rand
from ship import Ship
from port import Port
from shipyard import Shipyard
from shipowner import Shipowner

from colors import COLORS


class SeaMap:
    def __init__(self, nbr_ships, nbr_ports, nbr_shipyards, nbr_shipowners, map_size=700):
        self.map_size = map_size
        self.area = np.zeros((map_size, map_size))
        self.restricted_area = np.zeros((map_size, map_size, 3))
        self.ports = []
        self.shipyards = []
        self.ships = []
        self.shipowners = []
        self.nbr_ships = nbr_ships
        self.nbr_ports = nbr_ports
        self.nbr_shipyards = nbr_shipyards
        self.nbr_shipowners = nbr_shipowners

    def is_place_empty(self, coords, size_obj):
        obj_half_size = int(size_obj / 2) + 15
        return not np.any(self.restricted_area[coords[0]-obj_half_size:coords[0]+obj_half_size, coords[1]-obj_half_size:coords[1]+obj_half_size, :])

    def find_place(self, obj):
        while True:
            posX = rand(0+obj.size, self.map_size-obj.size)
            posY = rand(0+obj.size, self.map_size-obj.size)
            new_coords = [posX, posY]
            if self.is_place_empty(new_coords, obj.size):
                obj.position = new_coords
                self.area[new_coords[0], new_coords[1]] = 1
                self.draw_area(obj)
                break

    def draw_area(self, obj):
        coords = obj.position
        obj_half_size = int(obj.size / 2)
        if "shipyard" in obj.name:
            color = COLORS[2]
        elif "port" in obj.name:
            color = COLORS[1]
        elif "ship" in obj.name:
            # color = COLORS[0]
            if self.ships:
                if obj.name == self.ships[0].name:
                    color = COLORS[5]
                else:
                    color = obj.color
            else:
                color = obj.color
        else:
            color = COLORS[3]
        self.restricted_area[coords[0]-obj_half_size:coords[0]+obj_half_size, coords[1]-obj_half_size:coords[1]+obj_half_size, :] = color

    def place_ships(self):
        for ship_it in range(0, self.nbr_ships):
            capacity = rand(50, 1000)
            index = rand(0, self.nbr_shipowners - 1)
            shipowner = self.shipowners[index]
            seaCans = shipowner.schedule_seaCans(self)
            ship = Ship(name="ship"+str(ship_it), capacity=capacity, shipowner=shipowner, seaCans=seaCans)
            self.find_place(ship)
            self.ships.append(ship)

    def place_ports(self):
        for port_it in range(0, self.nbr_ports):
            port = Port(name="port"+str(port_it))
            port.create_docks(rand(1, 4))
            self.find_place(port)
            self.ports.append(port)

    def place_shipyards(self):
        for shipyard_it in range(0, self.nbr_shipyards):
            shipyard = Shipyard(name="shipyard"+str(shipyard_it))
            shipyard.create_docks(rand(2, 4))
            self.find_place(shipyard)
            self.shipyards.append(shipyard)

    def place_warehouses(self):
        for port in self.ports:
            port.create_warehouses(self)

    def setup_shipowners(self):
        for shipowner_it in range(0, self.nbr_shipowners):
            shipowner = Shipowner(nbr_seaCans=rand(5, 15))
            self.shipowners.append(shipowner)

    def clean_area(self):
        map_size = self.map_size
        self.restricted_area = np.zeros((map_size, map_size, 3))
        self.area = np.zeros((map_size, map_size))

    def update(self):
        self.nbr_ports = len(self.ports)
        self.nbr_ships = len(self.ships)
        self.nbr_shipyards = len(self.shipyards)
        self.nbr_shipowners = len(self.shipowners)

    def clean_map(self):
        self.nbr_ships = 0
        self.nbr_ports = 0
        self.nbr_shipyards = 0
        self.nbr_shipowners = 0

        self.ports = []
        self.ships = []
        self.shipyards = []
        self.shipowners = []

        self.clean_area()

    def init_map(self):
        self.setup_shipowners()
        self.place_shipyards()
        self.place_ports()
        self.place_ships()
        self.place_warehouses()




