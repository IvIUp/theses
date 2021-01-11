class Ship:
    def __init__(self, arrival_time, arrival_position):
        self.arrival_time = arrival_time
        self.arrival_position = arrival_position


shipDict = {}
with open("..\..\\visualisation\lockmasterApp\data\ships.txt", "r") as f:
    T = int(f.readline())
    number_of_ships = int(f.readline())
    print(T)
    for i, ship in enumerate(f):
        s = ship.split(', ')
        shipDict[f"ship{i + 1}"] = Ship(int(s[0]), int(s[1]))


arrival_times = []
arrival_positions = []

ships = list(shipDict.values())
for ship in ships:
    arrival_times.append(ship.arrival_time)
    arrival_positions.append(ship.arrival_position)
