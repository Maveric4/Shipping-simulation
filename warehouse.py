

class Warehouse:
    def __init__(self, name="Warehouse"):
        self.name = name
        self.capacity = 20
        self.seaCans = []
        self.nbr_of_seaCans = 0

    def load_seaCan(self, seaCan):
        self.seaCans.append(seaCan)
        self.nbr_of_seaCans += 1

    def unload_seaCan(self, seaCan):
        self.seaCans.remove(seaCan)
        self.nbr_of_seaCans -= 1


