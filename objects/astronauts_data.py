class AstronautsData():
    def __init__(self, astronauts=None, is_valid=False):
        if astronauts is None:
            astronauts = []
        self.astronauts = astronauts
        self.is_valid = is_valid
