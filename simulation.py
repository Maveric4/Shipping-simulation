from seaMap import SeaMap
from colors import COLORS
import time
import numpy as np
import cv2
import sys
import pickle
import csv
import os

TITLE_WINDOW = "Controls"
BUTTON_TRACKBAR_VAL = 0
SLIDER_MAX = 5
SLIDER_MAX_PORTS = 40
SLIDER_MAX_SHIPS = 100
SHIP_REFILL_FUEL_LEVEL = 10
SHIP_DAMAGED = 10


class Simulation:
    def __init__(self, args):
        self.map = SeaMap(args.NBR_SHIPS, args.NBR_PORTS, args.NBR_SHIPYARDS, args.NBR_SHIPOWNERS, args.MAP_SIZE)
        self.map.setup_shipowners()
        self.map.place_shipyards()
        self.map.place_ports()
        self.map.place_ships()
        self.map.place_warehouses()
        self.args = args
        self.step = 0

    def run(self):
        start_time = time.time()
        while self.step < self.args.NBR_STEPS:
            if len(self.map.ships) == 0:
                if self.args.verbose:
                    print("\nNo more ships. End of simulation")
                return False
            if self.step % 2 == 0:
                if not self.show_map():
                    if self.args.verbose:
                        print("\nPressed 'q'. End of simulation")
                    return False
            if time.time() - start_time > self.args.SIMULATION_TIME:
                self.step += 1
                self.next_step()
                start_time = time.time()
        return True

    def next_step(self):

        self.move_ships()
        self.give_orders()
        self.update_map()

    def move_ships(self):
        for ship in self.map.ships:
            if ship.fuel <= 0:
                if self.args.verbose:
                    print("{} destroyed. No fuel".format(ship.name))
                self.map.ships.remove(ship)
            if ship.state <= 0:
                if self.args.verbose:
                    print("{} destroyed. Damaged too much".format(ship.name))
                self.map.ships.remove(ship)
            if ship.is_waiting:
                ship.color = COLORS[-1] if ship.name != self.map.ships[0].name else COLORS[5]
                pass
            elif ship.is_going_to_dest_port and len(self.map.ships):
                ship.move_to_dest()
                ship.color = COLORS[-3] if ship.name != self.map.ships[0].name else COLORS[5]
            elif ship.is_going_to_src_port and len(self.map.ships):
                ship.move_to_src()
                ship.color = COLORS[-4] if ship.name != self.map.ships[0].name else COLORS[5]
            else:
                sys.exit()

    def give_orders(self):
        for ship in self.map.ships:
            if len(ship.dest_port_queue) == 1 or len(ship.seaCans) == 1:
                seaCans = ship.shipowner.schedule_seaCans(self.map)
                ship.seaCans.extend(seaCans)
                ship.get_port_queue()
            if ship.is_at_destiny_port() or ship.is_at_src_port():
                if ship.is_going_to_shipyard:
                    if ship.src_port_queue[0].has_empty_slots():
                        ship.src_port_queue[0].repair(ship)
                        ship.is_going_to_shipyard = False
                        ship.is_waiting = False
                    else:
                        ship.is_waiting = True
                elif ship.is_being_repaired:
                    if ship.src_port_queue[0].is_still_being_repaired(ship):
                        ship.is_waiting = True
                        if self.args.verbose:
                            print("{} is being repaired".format(ship.name))
                    else:
                        if self.args.verbose:
                            print("{} is repaired".format(ship.name))
                        ship.is_being_repaired = False
                        ship.is_waiting = False
                elif ship.state < SHIP_DAMAGED and ship.is_at_src_port():
                    if self.args.verbose:
                        print("{} going to the nearest shipyard".format(ship.name))
                    ship.go_to_nearest_shipyard(self.map.shipyards)
                else:
                    if ship.is_unloading_seaCan:
                        if ship.next_step_unload_seaCan():
                            ship.is_waiting = False
                            ship.is_unloading_seaCan = False
                            if ship.is_going_to_dest_port:
                                ship.is_going_to_dest_port = False
                                ship.is_going_to_src_ports = True
                                ship.get_next_dest_port(self.map, self.args.verbose)
                            else:
                                ship.is_going_to_src_ports = False
                                ship.is_going_to_dest_port = True
                                ship.get_next_src_port(self.map, self.args.verbose)
                        else:
                            ship.is_waiting = True
                    else:
                        ship.unload_seaCan()

            if ship.fuel < SHIP_REFILL_FUEL_LEVEL:
                ship.fill_up()
            # ship.print_info()

    def update_map(self):
        self.map.nbr_ships = self.args.NBR_SHIPS
        self.map.nbr_ports = self.args.NBR_PORTS
        self.map.nbr_shipyards = self.args.NBR_SHIPYARDS
        self.map.nbr_shipowners = self.args.NBR_SHIPOWNERS
        self.map.update()
        self.map.clean_area()
        for obj in self.map.ports:
            self.map.draw_area(obj)
        for obj in self.map.ships:
            self.map.draw_area(obj)
        for obj in self.map.shipyards:
            self.map.draw_area(obj)

    def show_map(self):
        img_map = np.array(self.map.restricted_area, dtype=np.uint8)
        img_map = self.print_labels(img_map)
        cv2.imshow("Shipping simulation", img_map)
        cv2.imshow("Controls", np.zeros((100, 350)))
        key = cv2.waitKey(1)
        if key == ord('q'):
            return False
        if key == ord('r'):
            self.on_button(0)
        elif key == ord('k'):
            self.args.SIMULATION_TIME -= 0.0005
        elif key == ord('l'):
            self.args.SIMULATION_TIME += 0.0005
        elif key == ord('s'):
            self.save_state()
            if self.args.verbose:
                print("State of simulation saved to pickle file")
        elif key == ord('g'):
            self.load_state()
            if self.args.verbose:
                print("State of simulation loaded from pickle file")
        elif key == ord('x'):
            self.save_state_in_csv()
            if self.args.verbose:
                print("State of simulation saved to csv file")
        elif key == ord('b'):
            self.load_state_from_csv()
            if self.args.verbose:
                print("State of simulation loaded from csv file")
        else:
            return True
        return True

    def print_labels(self, img_map):
        extra_padding_color = [15, 15, 15]
        top = 0
        # bottom = int(0.15 * img_map.shape[0])
        bottom = int(0.35 * img_map.shape[0])
        left = 0
        right = 0
        borderType = cv2.BORDER_CONSTANT
        img_map = cv2.copyMakeBorder(img_map, top, bottom, left, right, borderType, None, extra_padding_color)
        img_map[self.args.MAP_SIZE:self.args.MAP_SIZE + 5, :] = [255, 255, 255]
        dist_from_right_edge = 200
        dist_from_left_edge = 50
        cv2.putText(img_map, "Ships: {}".format(self.map.nbr_ships),
                    (int(self.args.MAP_SIZE - dist_from_right_edge), int(self.args.MAP_SIZE + bottom / 2 - 15)),
                    cv2.FONT_HERSHEY_PLAIN, 1, COLORS[0], 1)
        cv2.putText(img_map, "Ports: {}".format(self.map.nbr_ports),
                    (int(self.args.MAP_SIZE - dist_from_right_edge), int(self.args.MAP_SIZE + bottom / 2)),
                    cv2.FONT_HERSHEY_PLAIN, 1, COLORS[1], 1)
        cv2.putText(img_map, "Shipyards: {}".format(self.map.nbr_shipyards),
                    (int(self.args.MAP_SIZE - dist_from_right_edge), int(self.args.MAP_SIZE + bottom / 2 + 15)),
                    cv2.FONT_HERSHEY_PLAIN, 1, COLORS[2], 1)
        cv2.putText(img_map, "Shipowners: {}".format(self.map.nbr_shipowners),
                    (int(self.args.MAP_SIZE - dist_from_right_edge), int(self.args.MAP_SIZE + bottom / 2 + 30)),
                    cv2.FONT_HERSHEY_PLAIN, 1, COLORS[4], 1)
        cv2.putText(img_map, "{} State: {} Fuel: {}".format(self.map.ships[0].name,
                                                                  round(self.map.ships[0].state, 2),
                                                                  round(self.map.ships[0].fuel, 2)),
                    (int(dist_from_left_edge), int(self.args.MAP_SIZE + bottom / 2 - 15)), cv2.FONT_HERSHEY_PLAIN, 1,
                    COLORS[5], 1)
        cv2.putText(img_map, "Simulation step time {}".format(round(self.args.SIMULATION_TIME, 6)),
                    (int(dist_from_left_edge), int(self.args.MAP_SIZE + bottom / 2)), cv2.FONT_HERSHEY_PLAIN, 1,
                    COLORS[6], 1)
        cv2.putText(img_map, "Step {}".format(self.step),
                    (int(30), int(30),),
                    cv2.FONT_HERSHEY_PLAIN, 1, COLORS[4], 1)
        cv2.createTrackbar("Ships", TITLE_WINDOW, self.args.NBR_SHIPS, SLIDER_MAX_SHIPS, self.on_ships_trackbar)
        cv2.createTrackbar("Ports", TITLE_WINDOW, self.args.NBR_PORTS, SLIDER_MAX_PORTS, self.on_ports_trackbar)
        cv2.createTrackbar("Shipyards", TITLE_WINDOW, self.args.NBR_SHIPYARDS, SLIDER_MAX, self.on_shipyards_trackbar)
        cv2.createTrackbar("Shipowners", TITLE_WINDOW, self.args.NBR_SHIPOWNERS, SLIDER_MAX, self.on_shipowners_trackbar)
        cv2.createTrackbar("Apply", TITLE_WINDOW, BUTTON_TRACKBAR_VAL, 1, self.on_button)
        return img_map

    def on_button(self, val):
        global BUTTON_TRACKBAR_VAL
        BUTTON_TRACKBAR_VAL = 0
        self.map.clean_map()
        self.map.nbr_ships = self.args.NBR_SHIPS
        self.map.nbr_ports = self.args.NBR_PORTS
        self.map.nbr_shipyards = self.args.NBR_SHIPYARDS
        self.map.nbr_shipowners = self.args.NBR_SHIPOWNERS
        self.map.init_map()
        self.step = 0

    def on_ships_trackbar(self, val):
        if val > 1:
            self.args.NBR_SHIPS = val

    def on_ports_trackbar(self, val):
        if val > 2:
            self.args.NBR_PORTS = val

    def on_shipyards_trackbar(self, val):
        if val > 1:
            self.args.NBR_SHIPYARDS = val

    def on_shipowners_trackbar(self, val):
        if val > 1:
            self.args.NBR_SHIPOWNERS = val

    def save_state(self):
        if not os.path.isdir("./saved/"):
            os.mkdir("./saved/")
        with open("./saved/state.pkl", "wb") as state_file:
            state_dict = {"map": self.map, "args": self.args, "step": self.step}
            pickle.dump(state_dict, state_file, pickle.HIGHEST_PROTOCOL)

    def load_state(self):
        if not os.path.isfile("./saved/state.pkl"):
            print("No previous state of simulation saved in pickle")
            return None
        with open("./saved/state.pkl", "rb") as state_file:
            state_dict = pickle.load(state_file)
            self.map = state_dict["map"]
            self.args = state_dict["args"]
            self.step = state_dict["step"]

    def save_state_in_csv(self):
        if not os.path.isdir("./saved/"):
            os.mkdir("./saved/")
        with open("./saved/map.pkl", "wb") as map_file:
            pickle.dump(self.map, map_file, pickle.HIGHEST_PROTOCOL)

        with open('./saved/log.csv', mode='w', newline='') as state_file:
            csv_writer = csv.writer(state_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Param', 'Value'])
            csv_writer.writerow(['nbr_ships', self.args.NBR_SHIPS])
            csv_writer.writerow(['nbr_ports', self.args.NBR_PORTS])
            csv_writer.writerow(['nbr_shipyards', self.args.NBR_SHIPYARDS])
            csv_writer.writerow(['nbr_shipowners', self.args.NBR_SHIPOWNERS])
            csv_writer.writerow(['map_size', self.args.MAP_SIZE])
            csv_writer.writerow(['step', self.step])

    def load_state_from_csv(self):
        if not (os.path.isfile('./saved/log.csv') and os.path.isfile('./saved/map.pkl')):
            print("No previous state of simulation saved in csv")
            return None
        with open("./saved/map.pkl", "rb") as map_file:
            self.map = pickle.load(map_file)

        param_dict = {}
        with open('./saved/log.csv', mode='r', newline='') as state_file:
            csv_reader = csv.reader(state_file)
            for row in csv_reader:
                param_dict[row[0]] = row[1]

        self.args.NBR_SHIPS = int(param_dict['nbr_ships'])
        self.args.NBR_PORTS = int(param_dict['nbr_ports'])
        self.args.NBR_SHIPYARDS = int(param_dict['nbr_shipyards'])
        self.args.NBR_SHIPOWNERS = int(param_dict['nbr_shipowners'])
        self.args.map_size = int(param_dict['map_size'])
        self.step = int(param_dict['step'])
