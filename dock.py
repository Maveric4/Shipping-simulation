REPAIR_STEPS = 300


class Dock:
    def __init__(self, name):
        self.name = name
        self.docked_ship = None
        self.repair_step = 0
        self.is_empty = False

    def next_repair_step(self, ship):
        if self.repair_step < REPAIR_STEPS:
            self.repair_step += 1
            ship.state += 100/REPAIR_STEPS
            return True
        else:
            self.finish_repair()
            return False

    def finish_repair(self):
        self.repair_step = 0
        self.is_empty = True
        self.docked_ship = None

