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
        self.parameter = 'ESC'

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

        if key == glfw.KEY_X:
            population = self.community.get_populations()[self.background.select]
            population.restart()
            print(f'restart simulation!')

        if key == glfw.KEY_V:
            print('vista distancia social')

        if key == glfw.KEY_P:
            graph = self.background.graphs[0]
            pop = self.background.populations[self.background.select]
            for i, plot in enumerate(graph.plots):
                graph.update_plot(plot, pop.count[i], list(color_dict.keys())[i])

            fig, aux = plt.subplots(figsize=(10, 5))
            population = self.community.get_populations()[self.background.select]
            aux.plot(population.count[0], color='g', label='sanos')
            aux.plot(population.count[1], color='r', label='infectados')
            aux.plot(population.count[2], color='grey', label='muertos')
            aux.plot(population.count[3], color='b', label='recuperados')
            aux.set_xlabel(f'Tiempo [ite: {Person.iterations} ite = 1 dia]')
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

        if key == glfw.KEY_I:
            self.parameter = 'I'

        if key == glfw.KEY_R:
            self.parameter = 'R'

        if key == glfw.KEY_D:
            self.parameter = 'D'

        if key == glfw.KEY_H:
            self.parameter = 'H'

        if key == glfw.KEY_KP_ADD:
            if self.parameter == 'I':
                ite = Person.iterations
                prob = Person.parameters['prob_inf'] * ite
                Person.parameters['prob_inf'] += 0.05 / ite if (1 >= prob + 0.05) else (1-prob)/ite

            if self.parameter == 'R':
                radius = Person.parameters['radius']
                Person.parameters['radius'] += 0.01 if (0.2 >= radius + 0.01) else (0.2-radius)

            if self.parameter == 'D':
                ite = Person.iterations
                death_rate = Person.parameters['death_rate'] * ite
                Person.parameters['death_rate'] += 0.05 / ite if (1 >= death_rate + 0.05) else (1-death_rate)/ite

            if self.parameter == 'H':
                days = Person.parameters['days_to_heal']
                Person.parameters['days_to_heal'] += 1 if (14 >= days + 1) else (14 - days)

        if key == glfw.KEY_KP_SUBTRACT:
            if self.parameter == 'I':
                ite = Person.iterations
                prob = Person.parameters['prob_inf'] * ite
                Person.parameters['prob_inf'] += - 0.05 / ite if (prob - 0.05 >= 0) else (0-prob)/ite

            if self.parameter == 'R':
                radius = Person.parameters['radius']
                Person.parameters['radius'] += -0.01 if (radius - 0.01 >= 0) else (0 - radius)

            if self.parameter == 'D':
                ite = Person.iterations
                death_rate = Person.parameters['death_rate'] * ite
                Person.parameters['death_rate'] += - 0.05 / ite if (death_rate + 0.05 >= 0) else (0-death_rate)/ite

            if self.parameter == 'H':
                days = Person.parameters['days_to_heal']
                Person.parameters['days_to_heal'] += -1 if (days - 1 >= 0) else (0 - days)

        if key == glfw.KEY_ESCAPE:
            self.parameter = 'ESC'

    def set_community(self, community):
        self.community = community

    def set_background(self, background):
        self.background = background

    def on_scroll(self, window, pos, action):
        ite = Person.iterations
        prob = Person.parameters["prob_inf"] * ite
        Person.parameters["prob_inf"] += action * 0.1/ite if (1 >= prob + action * 0.1 >= 0) else 0
        print(Person.parameters["prob_inf"] * ite)
