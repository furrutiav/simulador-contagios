"""
F. Urrutia V., CC3501, 2020-1
-----------> CONTROLLER <-----------
        Control con el usuario
"""

from models import *
import glfw
from typing import Union
import sys


class Controller(object):
    def __init__(self):
        pass

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return

        if key == glfw.KEY_SPACE:
            pass
