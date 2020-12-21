"""
F. Urrutia V., CC3501, 2020-1
-----------> CONTROLLER <-----------
        Control con el usuario
"""

from models import *
import glfw


class Controller(object):
    def __init__(self):
        self.population: Population
        self.binary_value = True

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return
        if key == glfw.KEY_S:
            self.population.social_distance = not self.population.social_distance
            print(f'distancia social: {self.population.social_distance}')

        if key == glfw.KEY_SPACE:
            self.binary_value = not self.binary_value
            print(f'binary value: {self.binary_value}')

        if key == glfw.KEY_RIGHT:
            self.binary_value = not self.binary_value
            print(f'advance time (one day)!')

        if key == glfw.KEY_R:
            self.population.restart()
            print(f'restart simulation!')

    def set_population(self, population):
        self.population = population

    def on_scroll(self, window, pos, action):
        prob = Person.parameters["prob_inf"] * Person.iterations
        Person.parameters["prob_inf"] += action * 0.1/Person.iterations if (1 >= prob + action * 0.1 >= 0) else 0
        print(Person.parameters["prob_inf"] * Person.iterations)
