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
        self.community: Community
        self.background: Background
        self.binary_value = True

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return
        if key == glfw.KEY_S:
            population = self.community.get_populations()[self.background.select]
            population.social_distance = not population.social_distance
            self.background.buttons[0].set(int(population.social_distance))
            print(f'distancia social: {population.social_distance}')

        if key == glfw.KEY_SPACE:
            self.binary_value = not self.binary_value
            print(f'binary value: {self.binary_value}')

        if key == glfw.KEY_RIGHT:
            self.binary_value = not self.binary_value
            print(f'advance time (one day)!')

        if key == glfw.KEY_R:
            population = self.community.get_populations()[self.background.select]
            population.restart()
            print(f'restart simulation!')

        if key == glfw.KEY_P:
            fig, aux = plt.subplots(figsize=(10, 5))
            population = self.community.get_populations()[self.background.select]
            aux.plot(population.count[0], color='g', label='sanos')
            aux.plot(population.count[1], color='r', label='infectados')
            aux.plot(population.count[2], color='grey', label='muertos')
            aux.plot(population.count[3], color='b', label='recuperados')
            aux.set_xlabel('Tiempo [iter: 50 iter = 1 dia]')
            aux.set_ylabel('Individuos [#]')
            aux.set_ylim(0, population.size)
            aux.set_title(f'Estado población #{self.background.select+1}')
            aux.grid()
            aux.legend()
            plt.subplots_adjust(wspace=0, hspace=0)
            plt.show()

        if key == glfw.KEY_1 or key == glfw.KEY_UP:
            self.background.set_select(0)
            self.background.buttons[0].set(int(self.community.get_populations()[0].social_distance))
            print('select #1')

        if key == glfw.KEY_2 or key == glfw.KEY_DOWN:
            self.background.set_select(1)
            self.background.buttons[0].set(int(self.community.get_populations()[1].social_distance))
            print('select #2')

    def set_community(self, community):
        self.community = community

    def set_background(self, background):
        self.background = background

    def on_scroll(self, window, pos, action):
        prob = Person.parameters["prob_inf"] * Person.iterations
        Person.parameters["prob_inf"] += action * 0.1/Person.iterations if (1 >= prob + action * 0.1 >= 0) else 0
        print(Person.parameters["prob_inf"] * Person.iterations)
