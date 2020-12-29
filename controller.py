"""
F. Urrutia V., CC3501, 2020-1
-----------> CONTROLLER <-----------
        Control con el usuario
"""

from models import *
import glfw
import numpy as np
import matplotlib.pyplot as plt


class Controller(object):
    def __init__(self):
        self.population: Population
        self.background: Background
        self.binary_value = True

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return
        if key == glfw.KEY_S:
            self.population.social_distance = not self.population.social_distance
            self.background.buttons[0].set(int(self.population.social_distance))
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

        if key == glfw.KEY_P:
            global time
            fig, aux = plt.subplots(figsize=(10, 5))
            aux.plot(self.population.count[0], color='g', label='sanos')
            aux.plot(self.population.count[1], color='r', label='infectados')
            aux.plot(self.population.count[2], color='grey', label='muertos')
            aux.plot(self.population.count[3], color='b', label='recuperados')
            aux.set_ylim(0, self.population.size)
            aux.set_title('Estado población #1')
            aux.legend()
            plt.show()

        if key == glfw.KEY_1:
            self.background.set_select(0)
            print('select #1')

        if key == glfw.KEY_2:
            self.background.set_select(1)
            print('select #2')

    def set_population(self, population):
        self.population = population

    def set_background(self, background):
        self.background = background

    def on_scroll(self, window, pos, action):
        prob = Person.parameters["prob_inf"] * Person.iterations
        Person.parameters["prob_inf"] += action * 0.1/Person.iterations if (1 >= prob + action * 0.1 >= 0) else 0
        print(Person.parameters["prob_inf"] * Person.iterations)
