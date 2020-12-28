"""
F. Urrutia V., CC3501, 2020-1
-----------> MODELS <-----------
Modelos:
Builder, Person, Population
"""
from libs import basic_shapes as bs, transformations as tr, easy_shaders as es, scene_graph as sg
import numpy as np
from OpenGL.GL import *
import random as rd
from scipy.stats import bernoulli, norm, uniform
from scipy.spatial import distance
from typing import Union, List, Any
import json
from multiprocessing import Process, Pool
from numba import njit, prange

# load virus
virus = open('virus.json')
data_virus = json.load(virus)[0]
# init time
time = 0

color_dict = {'g': (0, 1, 0), 'r': (1, 0, 0), 'grey': (0.4, 0.4, 0.4), 'b': (0, 0, 1)}

width, height = 1000, 1000


class Builder(object):
    def __init__(self):
        self._gpu_models = [
            es.toGPUShape(bs.createColorQuad(0, 1, 0)),
            es.toGPUShape(bs.createColorQuad(1, 0, 0)),
            es.toGPUShape(bs.createColorQuad(0.4, 0.4, 0.4)),
            es.toGPUShape(bs.createColorQuad(0, 0, 1))
        ]
        self._graph = []
        for i in range(4):
            node = sg.SceneGraphNode(f'base_node_{i}')
            node.childs += [self._gpu_models[i]]

            self._graph += [node]

    def get_graph(self):
        return self._graph


class Person(object):
    iterations = 50
    parameters = {
        "status": {"sano": 0, "infectado": 1, "muerto": 2, "recuperado": 3},
        "prob_inf": data_virus['Contagious_prob'] / iterations,
        "ratio_inf": 0.1,
        "radius": data_virus['Radius'],
        "death_rate": data_virus['Death_rate'] / iterations,
        "days_to_heal": data_virus['Days_to_heal'] * iterations,
        "prob_social_distance": 0.5

    }

    def __init__(self, builder, index, group=0):
        self.social_distance = bernoulli.rvs(self.parameters["prob_social_distance"])
        self.index = index
        self.group = group
        self.log_pos = tuple([[np.random.normal(0, 0.2) for _ in range(2)],
                              get_rvs_circular(0.6, 0.15)][group])
        self.status = bernoulli.rvs(self.parameters["ratio_inf"])
        self.builder = builder
        self.neighbors_visited = []
        self.day_zero = -1 if self.status == 0 else 0

        node = sg.SceneGraphNode(f'person_{index}')
        node.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1 / 50)
        ])
        node.childs += [self.builder.get_graph()[self.status]]

        self.model = node

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update_pos(self):
        global time
        flow = [self.circular_flow(1), self.circular_flow(-1)][self.group]
        new_pos = [np.random.normal(0.01 * flow[i], 0.002) + self.log_pos[i] for i in range(2)]
        if -1 < new_pos[0] < 1 and -1 < new_pos[1] < 1:
            self.log_pos = new_pos
        self.model.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1 / 50)
        ])

    def update_status(self, other=None, dif=(0, 0)):
        aux = self.status
        self.death()
        if other:
            self.infect(other, dif)
        if aux != self.status:
            self.model.childs = [self.builder.get_graph()[self.status]]

    def infect(self, other, dif):
        if other:
            d = get_norm(dif)
            r = self.parameters["radius"]
            if d < r:
                self.status = bernoulli.rvs(self.parameters["prob_inf"])

    def apply_social_distance(self, other, active, dif, dist=1.5):
        if active:
            if other:
                d = get_norm(dif)
                s = [dif[i] / d for i in range(2)] if d > 0 else (0, 0)
                r = self.parameters["radius"]
                if d < dist * r:
                    if self.social_distance == 1:
                        new_pos = tuple([0.1 * 1.5 * r * s[i] * 0.5 + self.log_pos[i] for i in range(2)])
                        if -1 < new_pos[0] < 1 and -1 < new_pos[1] < 1:
                            self.log_pos = new_pos
                    if other.social_distance == 1:
                        new_pos = tuple([0.1 * 1.5 * r * (-s[i]) * 0.5 + other.log_pos[i] for i in range(2)])
                        if -1 < new_pos[0] < 1 and -1 < new_pos[1] < 1:
                            other.log_pos = new_pos

    def death(self):
        global time
        if self.status == 1:
            if time - self.day_zero == self.parameters["days_to_heal"]:
                self.status = 3
            else:
                self.status = 1 + bernoulli.rvs(self.parameters["death_rate"])

    def get_model(self):
        return self.model

    def get_log_pos(self):
        return self.log_pos

    def get_status(self):
        return self.status

    def set_visited(self, size):
        self.neighbors_visited = [0 for _ in range(size)]

    def set_visit(self, index_other):
        self.neighbors_visited[index_other] = 1

    def is_visited(self, index_other):
        return self.neighbors_visited[index_other]

    def is_cell(self, cell):
        return bool([cell[i][0] <= self.log_pos[i] <= cell[i][1] for i in range(2)])

    def set_prob_inf(self, prob):
        self.parameters["prob_inf"] = prob / self.iterations

    def set_day_zero(self):
        global time
        self.day_zero = time + 1

    def circular_flow(self, om=1):
        global time
        r = get_norm(self.log_pos)
        theta = get_angle(self.log_pos)
        vx = - om * r * np.sin(theta)
        vy = om * r * np.cos(theta)
        return vx, vy


class Population(object):

    def __init__(self, builder, size, social_distance=False, groups=1, view_center=(0, 0)):
        self.builder = builder
        self.groups = groups
        self.size = size
        self.social_distance = social_distance
        self.view_center = view_center

        root = sg.SceneGraphNode('root')
        root.transform = tr.matmul([
            tr.translate(view_center[0], view_center[1], 0),
            tr.uniformScale(0.4)
        ])
        root.childs = []

        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        self.r_people = []
        for k in range(size):
            person_k = Person(builder, k, 0) if k < size / groups else Person(builder, k, 1)
            person_k.set_visited(size)
            if person_k.get_status():
                self.i_people.append(person_k)
            else:
                self.s_people.append(person_k)
            root.childs += [person_k.get_model()]
        self.people += self.s_people + self.i_people

        self.count = [[len(people)] for people in [self.s_people, self.i_people, self.d_people, self.r_people]]

        self.model = root

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update(self):
        global time
        for i_person in self.i_people:
            i_person.update_pos()
            i_person.update_status()
            if i_person.get_status() - 1:
                self.d_people += [i_person]
                self.i_people.remove(i_person)
                print('+1 muerto')

        for s_person in self.s_people:
            active = self.social_distance
            for i_person in self.i_people:
                dif = np.subtract(s_person.get_log_pos(), i_person.get_log_pos())
                s_person.apply_social_distance(i_person, active, dif)
                s_person.update_status(i_person, dif)
                if s_person.get_status():
                    self.i_people += [s_person]
                    self.s_people.remove(s_person)
                    print('+1 infectado')
                    break
            for s2_person in self.s_people:
                dif = np.subtract(s_person.get_log_pos(), s2_person.get_log_pos())
                s_person.apply_social_distance(s2_person, active, dif)

            s_person.update_pos()
        print(f'sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}') \
            if not time % 100 else None
        time += 1

    def update_grid_smart(self, mode=3):
        global time
        s_people = self.s_people
        i_people = self.i_people
        d_people = self.d_people
        r_people = self.r_people
        active = self.social_distance
        p_index = 0
        for person in self.people:
            if (not person.is_visited(p_index)) and (person.get_status() in [0, 1, 3]):
                if person.get_status() == 1:
                    person.update_status()
                    if person.get_status() == 3:
                        r_people += [person]
                        i_people.remove(person)
                        print('+1 recuperado')
                        break
                    elif person.get_status() == 2:
                        d_people += [person]
                        i_people.remove(person)
                        print('+1 muerto')
                        break
                person.set_visit(p_index)
                p_log_pos = person.get_log_pos()
                cell = get_individual_n_grid(mode, p_log_pos)
                p2_index = 0
                for person2 in self.people:
                    if not person.is_visited(p2_index):
                        person.set_visit(p2_index)
                        person2.set_visit(p_index)
                        if person2.is_cell(cell):
                            dif = get_dif(p_log_pos, person2.get_log_pos())
                            person.apply_social_distance(person2, active, dif)
                            if person.get_status() == 0 and person2.get_status() == 1:
                                person.update_status(person2, dif)
                                if person.get_status() == 1:
                                    person.set_day_zero()
                                    i_people += [person]
                                    s_people.remove(person)
                                    print('+1 infectado')
                                    break
                            elif person.get_status() == 1 and person2.get_status() == 0:
                                person2.update_status(person, dif)
                                if person2.get_status() == 1:
                                    person2.set_day_zero()
                                    i_people += [person2]
                                    s_people.remove(person2)
                                    print('+1 infectado')
                                    break
                    p2_index += 1
                person.update_pos()
                if person.get_status() in [0, 3]:
                    person.set_visited(self.size)
            p_index += 1
        self.s_people = s_people
        self.i_people = i_people
        self.d_people = d_people
        self.r_people = r_people
        for i_person in self.i_people:
            i_person.set_visited(self.size)
        self.show_data()
        for index, people in enumerate([self.s_people, self.i_people, self.d_people, self.r_people]):
            self.count[index].append(len(people))
        time += 1

    def show_data(self):
        global time
        if not time % 100:
            print(f'sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}, '
                  f'recuperados: {len(self.r_people)}')

    def update_forward(self):
        for _ in range(Person.iterations):
            self.update_grid_smart()

    def restart(self):
        root = sg.SceneGraphNode('root')
        root.transform = tr.matmul([
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.5)
        ])
        root.childs = []

        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        self.r_people = []
        for k in range(self.size):
            person_k = Person(self.builder, k, 0) if k < self.size / self.groups else Person(self.builder, k, 1)
            person_k.set_visited(self.size)
            if person_k.get_status():
                self.i_people.append(person_k)
            else:
                self.s_people.append(person_k)
            root.childs += [person_k.get_model()]
        self.people += self.s_people + self.i_people

        self.model = root


class Community(object):
    def __init__(self, pop1, pop2):
        self.pop1 = pop1
        self.pop2 = pop2

    def update(self):
        self.pop1.update_grid_smart()
        self.pop2.update_grid_smart()

    def update_forward(self):
        self.pop1.update_forward()
        self.pop2.update_grid_smart()

    def draw(self, pipeline):
        self.pop1.draw(pipeline)
        self.pop2.draw(pipeline)


class Background(object):
    def __init__(self, pop1):
        self.population = pop1
        square_gpu = es.toGPUShape(bs.createColorQuad(0.05, 0.07, 0.11))

        square1 = sg.SceneGraphNode('square1')
        square1.transform = tr.matmul([
            tr.translate(0.5, 0.5, 0),
            tr.uniformScale(0.8)
        ])
        square1.childs += [square_gpu]

        square2 = sg.SceneGraphNode('square2')
        square2.transform = tr.matmul([
            tr.translate(0.5, -0.5, 0),
            tr.uniformScale(0.8)
        ])
        square2.childs += [square_gpu]

        squares = sg.SceneGraphNode('squares')
        squares.childs += [square1, square2]

        self.bars = []
        self.model = squares

        for i, c in enumerate(color_dict.keys()):
            self.set_percent_bar(color=c, center=(-0.5, (2-i) * 0.05 + 0.025 + 0.5))

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def set_percent_bar(self, value=0, size=(0.5, 0.05), center=(0, 0), color='g'):
        pB = PercentBar(value, size, center, color)
        self.bars.append(pB)
        self.model.childs += [pB.get()]

    def update(self):
        for i, b in enumerate(self.bars):
            b.set(self.population.count[i][-1] / 100)


class PercentBar(object):

    def __init__(self, value, size, center, color):
        self.value = value
        in_bar_gpu = es.toGPUShape(apply_tuple(bs.createColorQuad)(color_dict[color]))
        out_bar_gpu = es.toGPUShape(bs.createColorQuad(0.05, 0.07, 0.11))

        out_bar = sg.SceneGraphNode('out_bar')
        out_bar.childs += [out_bar_gpu]

        in_bar = sg.SceneGraphNode('in_bar')
        in_bar.transform = tr.matmul([
            tr.translate((value - 1) / 2, 0, 0),
            tr.scale(value, 1, 1)
        ])
        in_bar.childs += [in_bar_gpu]

        center = center[0], center[1], 0
        size = size[0], size[1], 1

        bar = sg.SceneGraphNode('bar')
        bar.transform = tr.matmul([
            apply_tuple(tr.translate)(center),
            apply_tuple(tr.scale)(size)
        ])
        bar.childs += [in_bar, out_bar]

        self.in_bar = in_bar
        self.model = bar

    def set(self, value):
        self.in_bar.transform = tr.matmul([
            tr.translate((value - 1) / 2, 0, 0),
            tr.scale(value, 1, 1)
        ])

    def get(self):
        return self.model


def get_dif(vec1, vec2):
    return [vec1[i] - vec2[i] for i in range(2)]


def get_norm(vec):
    return sum([vec[i] ** 2 for i in range(2)]) ** 0.5


def get_individual_n_grid(n, log_pos):
    return [(log_pos[i] - 1 / n, log_pos[i] + 1 / n) for i in range(2)]


def get_grid_n_ary(n):
    grid_out = []
    for j in range(n):
        row = []
        for i in range(n):
            row += [[(-1 + (2 / n) * i, -1 + (2 / n) * (i + 1)), (1 - (2 / n) * (j + 1), 1 - (2 / n) * j)]]
        grid_out += row
    return grid_out


def get_angle(log_pos):
    return np.arctan2(log_pos[1], log_pos[0])


def get_rvs_circular(loc, scale):
    r = norm.rvs(loc, scale)
    theta = uniform.rvs(0, 2 * np.pi)
    return [r * np.sin(theta), r * np.cos(theta)]


apply_tuple = lambda f: lambda args: f(*args)
