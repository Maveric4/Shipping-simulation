

class SeaCan:
    def __init__(self, source_port, destination_port, content=None):
        self.position = [0, 0]
        self.source_port = source_port
        self.destination_port = destination_port # ["", 1]
        self.content = content
        self.price = self.calc_price()

    def calc_price(self):
        return 50



