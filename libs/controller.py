"""
F. Urrutia V., CC3501, 2020-1
-----------> CONTROLLER <-----------
        Control con el usuario
"""

from libs.models import *
import glfw
import matplotlib.pyplot as plt


class Controller(object):
    def __init__(self):
        self.community: Community
        self.background: Background
        self.binary_value = True
        self.parameter = 'ESC'
        self.view = False
        self.mask = True

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

        if key == glfw.KEY_P:
            self.parameter = 'P'
            self.mask = False
            graph = self.background.graphs[0]
            pop = self.background.populations[self.background.select]
            for i, plot in enumerate(graph.plots):
                graph.update_plot(plot, pop.count[i], list(color_dict.keys())[i], max(pop.size, 100))

        if key == glfw.KEY_1:
            self.background.set_select(0)
            population = self.community.get_populations()[self.background.select]
            self.background.buttons[0].set(int(population.social_distance))
            self.background.buttons[1].set(int(population.quarantine))
            self.background.buttons[2].set(int(population.migration))
            print('select #1')

        if key == glfw.KEY_2:
            self.background.set_select(1)
            population = self.community.get_populations()[self.background.select]
            self.background.buttons[0].set(int(population.social_distance))
            self.background.buttons[1].set(int(population.quarantine))
            self.background.buttons[2].set(int(population.migration))
            print('select #2')

        if key == glfw.KEY_I:
            self.parameter = 'I'

        if key == glfw.KEY_R:
            self.parameter = 'R'

        if key == glfw.KEY_D:
            self.parameter = 'D'

        if key == glfw.KEY_H:
            self.parameter = 'H'

        if key == glfw.KEY_A:
            self.parameter = 'A'

        if key == glfw.KEY_Q:
            self.parameter = 'Q'

        if key == glfw.KEY_N:
            self.parameter = 'N'

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

            if self.parameter == 'A':
                ratio = Person.parameters['ratio_social_distance']
                Person.parameters['ratio_social_distance'] += 0.05 if (1 >= ratio + 0.05) else (1 - ratio)
                pop = self.community.get_populations()[self.background.select]
                pop.update_social_distance(status='+')
                pop.view_social_distance(self.view)

            if self.parameter == 'Q':
                days = Person.parameters['days_to_quarantine']
                Person.parameters['days_to_quarantine'] += 1 if (14 >= days + 1) else (14 - days)

            if self.parameter == 'N':
                ite = Person.iterations
                migration_rate = Person.parameters['migration_rate'] * ite
                Person.parameters['migration_rate'] += 0.05 / ite if (1 >= migration_rate + 0.05) else (1-migration_rate)/ite

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
                Person.parameters['death_rate'] += - 0.05 / ite if (death_rate - 0.05 >= 0) else (0-death_rate)/ite

            if self.parameter == 'H':
                days = Person.parameters['days_to_heal']
                Person.parameters['days_to_heal'] += -1 if (days - 1 >= 0) else (0 - days)

            if self.parameter == 'A':
                ratio = Person.parameters['ratio_social_distance']
                Person.parameters['ratio_social_distance'] += -0.05 if (ratio - 0.05 >= 0) else (0 - ratio)
                pop = self.community.get_populations()[self.background.select]
                pop.update_social_distance(status='-')
                pop.view_social_distance(self.view)

            if self.parameter == 'Q':
                days = Person.parameters['days_to_quarantine']
                Person.parameters['days_to_quarantine'] += -1 if (days - 1 >= 0) else (0 - days)

            if self.parameter == 'N':
                ite = Person.iterations
                migration_rate = Person.parameters['migration_rate'] * ite
                Person.parameters['migration_rate'] += - 0.05 / ite if (migration_rate - 0.05 >= 0) else (0-migration_rate)/ite

        if key == glfw.KEY_V:
            pop = self.community.get_populations()[self.background.select]
            self.view = not self.view
            pop.view_social_distance(self.view)
            print(f'vista distancia social:{self.view}')

        if key == glfw.KEY_ESCAPE:
            self.parameter = 'ESC'

        if key == glfw.KEY_M:
            population = self.community.get_populations()[self.background.select]
            population.migration = not population.migration
            self.background.buttons[2].set(int(population.migration))
            print(f'migration: {population.migration}')

        if key == glfw.KEY_C:
            population = self.community.get_populations()[self.background.select]
            population.quarantine = not population.quarantine
            self.background.buttons[1].set(int(population.quarantine))
            print(f'quarantine: {population.quarantine}')

    def plot(self):
        pop = self.background.populations[self.background.select]
        fig, aux = plt.subplots(figsize=(10, 5))
        aux.plot(pop.count[0], color='g', label='sanos')
        aux.plot(pop.count[1], color='r', label='infectados')
        aux.plot(pop.count[2], color='grey', label='muertos')
        aux.plot(pop.count[3], color='b', label='recuperados')
        aux.set_xlabel(f'Tiempo [ite: {Person.iterations} ite = 1 dia]')
        aux.set_ylabel('Individuos [#]')
        aux.set_ylim(0, max(pop.size, 100))
        aux.set_title(f'Estado población #{self.background.select + 1}')
        aux.grid()
        aux.legend()
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()
        self.parameter = 'ESC'

    def set_community(self, community):
        self.community = community

    def set_background(self, background):
        self.background = background
