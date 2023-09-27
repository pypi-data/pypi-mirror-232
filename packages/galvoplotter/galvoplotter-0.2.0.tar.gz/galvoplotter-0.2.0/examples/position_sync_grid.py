"""
Creates a 15x15 grid of locations turning the laser on for half a second in each location.
"""

from galvo.controller import GalvoController

controller = GalvoController("default.json")
with controller.lighting() as c:
    for x in range(0x1000, 0xFFFF, 0x1000):
        for y in range(0x1000, 0xFFFF, 0x1000):
            c.dark(x, y)
            c.light_on()
            c.wait(500)
