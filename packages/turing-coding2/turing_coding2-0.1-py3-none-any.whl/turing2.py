from coding2 import *
from functools import partial


class Player:
    def __init__(self):
        pass

class Screen:
    def __init__(self):
        pass

player_functions = {
    "turnLeft": partial(turnLeft),
    "turnRight": partial(turnRight),
    "movesForward": partial(movesForward),
    "putDown": partial(putDown),
    "isGo": partial(isGo),
    "shape": partial(shape),
}

screen_functions = {
    "loadMap": partial(loadMap),
    "mapInput": partial(mapInput),
    "bgpic": partial(bgpic),
    "exit": partial(exit),
    "restart": partial(restart)
}

for func_name, func in player_functions.items():
    setattr(Player, func_name, func)

for func_name, func in screen_functions.items():
    setattr(Screen, func_name, func)

