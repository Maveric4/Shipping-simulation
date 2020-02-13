import numpy as np
from random import random, randint as rand
from colors import COLORS


class Ship:
    def __init__(self, name, capacity, shipowner, seaCans):
        self.position = [0, 0]
        self.seaCans = seaCans
        self.src_port_queue = []
        self.dest_port_queue = []
        self.shipowner = shipowner
        self.capacity = capacity
        self.fuel = 20
        self.state = 100
        self.name = name
        self.size = 10
        self.color = COLORS[0]
        self.is_waiting = False
        self.is_at_dock = False
        self.is_going_to_shipyard = False
        self.is_being_repaired = False
        self.get_port_queue()
        self.is_going_to_src_port = True
        self.is_going_to_dest_port = False
        self.unloading_step = 0
        self.is_unloading_seaCan = False

    def get_port_queue(self):
        for seaCan in self.seaCans:
            self.src_port_queue.append(seaCan.source_port)
            self.dest_port_queue.append(seaCan.destination_port)

    def degrade(self):
        if rand(0, 1000) == 100:
            self.state = 7
        else:
            self.state -= random() * 0.02 # 0.1

    def use_fuel(self):
        self.fuel -= (random() * 0.03 + 0.01)
    
    def move_to_dest(self):
        dest_pos = self.dest_port_queue[0].position
        if self.position[1] != displ_pos(dest_pos[1], self.dest_port_queue[0].size):
            if self.position[1] < displ_pos(dest_pos[1], self.dest_port_queue[0].size):
                self.position = [self.position[0], self.position[1] + 1]
            else:
                self.position = [self.position[0], self.position[1] - 1]
        if self.position[0] != displ_pos(dest_pos[0], self.dest_port_queue[0].size):
            if self.position[0] < displ_pos(dest_pos[0], self.dest_port_queue[0].size):
                self.position = [self.position[0] + 1, self.position[1]]
            else:
                self.position = [self.position[0] - 1, self.position[1]]
        self.use_fuel()
        self.degrade()

    def move_to_src(self):
        src_pos = self.src_port_queue[0].position
        if self.position[1] != displ_pos(src_pos[1], self.src_port_queue[0].size):
            if self.position[1] < displ_pos(src_pos[1], self.src_port_queue[0].size):
                self.position = [self.position[0], self.position[1] + 1]
            else:
                self.position = [self.position[0], self.position[1] - 1]
        if self.position[0] != displ_pos(src_pos[0], self.src_port_queue[0].size):
            if self.position[0] < displ_pos(src_pos[0], self.src_port_queue[0].size):
                self.position = [self.position[0] + 1, self.position[1]]
            else:
                self.position = [self.position[0] - 1, self.position[1]]
        self.use_fuel()
        self.degrade()

    def get_next_dest_port(self, seaMap, verbose):
        old_port = self.dest_port_queue.pop(0)
        if verbose:
            print("Ship: {} arrived to: {} ! New port is: {}".format(self.name, old_port.name, self.dest_port_queue[0].name))

    def get_next_src_port(self, seaMap, verbose):
        old_port = self.src_port_queue.pop(0)
        if verbose:
            print("Ship: {} arrived to: {} ! New port is: {}".format(self.name, old_port.name,
                                                                     self.dest_port_queue[0].name))

    def is_at_destiny_port(self):
        dest_pos = self.dest_port_queue[0].position
        return (self.position[0] == displ_pos(dest_pos[0], self.dest_port_queue[0].size)) and (
                self.position[1] == displ_pos(dest_pos[1], self.dest_port_queue[0].size))

    def is_at_src_port(self):
        dest_pos = self.src_port_queue[0].position
        return (self.position[0] == displ_pos(dest_pos[0], self.src_port_queue[0].size)) and (
                self.position[1] == displ_pos(dest_pos[1], self.src_port_queue[0].size))

    def fill_up(self):
        current_port = self.dest_port_queue[0]
        current_port.fill_up_ship(self)

    def go_to_nearest_shipyard(self, shipyards):
        index, nearest_shipyard = min(enumerate(shipyards), key=lambda shipyard: calc_dist(shipyard[1].position, self.position))
        # print(nearest_shipyard.position)
        self.src_port_queue.insert(0, nearest_shipyard)
        self.is_going_to_shipyard = True

    def print_info(self):
        print("Ship: {} Fuel: {} State: {} Capacity: {}".format(self.name, round(self.fuel, 2), round(self.state, 2), self.capacity))

    def unload_seaCan(self):
        self.is_unloading_seaCan = True
        current_port = self.dest_port_queue[0]
        current_port.loading_warehouse.load_seaCan(self.seaCans.pop(0))

    def next_step_unload_seaCan(self):
        self.unloading_step += 1
        if self.unloading_step == 50:
            self.unloading_step = 0
            return True
        else:
            return False


def displ_pos(pos, port_size):
    return pos - int(port_size / 2 + 3)


def calc_dist(pos_shipyard, pos_ship):
    return np.linalg.norm(np.array([pos_ship[0]-pos_shipyard[0], pos_ship[1]-pos_shipyard[1]]))

