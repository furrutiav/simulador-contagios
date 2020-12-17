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
from scipy.stats import bernoulli, norm
from scipy.spatial import distance
from typing import Union, List, Any

c = 0

border_radius = 0.05

grid = {
    "binary": [
        [(-1, 0), (0, 1)], [(0, 1), (0, 1)],
        [(-1, 0), (-1, 0)], [(0, 1), (-1, 0)]
    ],
    "ternary": [
        [(-1, -1 / 3), (1 / 3, 1)], [(-1 / 3, 1 / 3), (1 / 3, 1)], [(1 / 3, 1), (1 / 3, 1)],
        [(-1, -1 / 3), (-1 / 3, 1 / 3)], [(-1 / 3, 1 / 3), (-1 / 3, 1 / 3)], [(1 / 3, 1), (-1 / 3, 1 / 3)],
        [(-1, -1 / 3), (-1, -1 / 3)], [(-1 / 3, 1 / 3), (-1, -1 / 3)], [(1 / 3, 1), (-1, -1 / 3)]
    ],
    "quaternary": [
        [(-1.0, -0.5), (0.5, 1.0)], [(-0.5, 0.0), (0.5, 1.0)], [(0.0, 0.5), (0.5, 1.0)], [(0.5, 1.0), (0.5, 1.0)],
        [(-1.0, -0.5), (0.0, 0.5)], [(-0.5, 0.0), (0.0, 0.5)], [(0.0, 0.5), (0.0, 0.5)], [(0.5, 1.0), (0.0, 0.5)],
        [(-1.0, -0.5), (-0.5, 0.0)], [(-0.5, 0.0), (-0.5, 0.0)], [(0.0, 0.5), (-0.5, 0.0)], [(0.5, 1.0), (-0.5, 0.0)],
        [(-1.0, -0.5), (-1.0, -0.5)], [(-0.5, 0.0), (-1.0, -0.5)], [(0.0, 0.5), (-1.0, -0.5)], [(0.5, 1.0), (-1.0, -0.5)]
    ],
    "border": [
        [(-border_radius, border_radius), (1/3+border_radius, 1)],
        [(-border_radius, border_radius), (1/3-border_radius, 1/3+border_radius)],
        [(-border_radius, border_radius), (-1/3+border_radius, 1/3-border_radius)],
        [(-border_radius, border_radius), (-1/3-border_radius, -1/3+border_radius)],
        [(-border_radius, border_radius), (-1, -1/3-border_radius)],
        [(-1, -1/3-border_radius), (-border_radius, border_radius)],
        [(-1/3-border_radius, -1/3+border_radius), (-border_radius, border_radius)],
        [(-1/3+border_radius, 1/3-border_radius), (-border_radius, border_radius)],
        [(1/3-border_radius, 1/3+border_radius), (-border_radius, border_radius)],
        [(1/3+border_radius, 1), (-border_radius, border_radius)]

    ],
    "dict_border": {
        0: [(-1 / 3, 1 / 3), (1 / 3, 1)], 1: [(-1 / 3, 1 / 3), (-1 / 3, 1)], 2: [(-1 / 3, 1 / 3), (-1 / 3, 1/3)],
        3: [(-1 / 3, 1 / 3), (-1, 1/3)], 4: [(-1 / 3, 1 / 3), (-1, -1/3)],
        5: [(-1, -1 / 3), (-1 / 3, 1 / 3)], 6: [(-1, 1 / 3), (-1 / 3, 1 / 3)], 7: [(-1 / 3, 1 / 3), (-1 / 3, 1 / 3)],
        8: [(-1 / 3, 1), (-1 / 3, 1 / 3)], 9: [(1 / 3, 1), (-1 / 3, 1 / 3)]
    }
}


def get_grid_n_ary(n):
    grid_out = []
    for j in range(n):
        row = []
        for i in range(n):
            row += [[(-1 + (2 / n) * i, -1 + (2 / n) * (i+1)), (1 - (2 / n) * (j+1), 1 - (2 / n) * j)]]
        grid_out += row
    return grid_out


# print(get_grid_n_ary(4))


class Builder(object):
    def __init__(self):
        self._gpu_models = [
            es.toGPUShape(bs.createColorQuad(0, 1, 0)),
            es.toGPUShape(bs.createColorQuad(1, 0, 0)),
            es.toGPUShape(bs.createColorQuad(0, 0, 1))
        ]
        self._graph = []
        for i in range(3):
            node = sg.SceneGraphNode(f'base_node_{i}')
            node.childs += [self._gpu_models[i]]

            self._graph += [node]

    def get_graph(self):
        return self._graph


class Person(object):
    parameters = {
        "status": {"sano": 0, "infectado": 1, "muerto": 2},
        "prob_inf": 0.2 / 50,
        "ratio": 0.2,
        "radius": 0.05,
        "death_rate": 0.1 / 50
    }

    def __init__(self, builder, index, group=0):
        self.index = index
        self.group = group
        self.log_pos = tuple([[np.random.normal(-0.1, 0.1) for _ in range(2)],
                              [np.random.uniform(-1, 1) for _ in range(2)]][group])
        self.status = bernoulli.rvs(self.parameters["ratio"])
        self.builder = builder
        self.neighbors_visited = []

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
        global c
        alpha = 0.04
        flow = [(np.cos(c * alpha), np.sin(c * alpha)), (-self.log_pos[0], -self.log_pos[1])][self.group]
        new_pos = tuple([[np.random.normal(0.01 * flow[i], 0.005) + self.log_pos[i] for i in range(2)],                # [np.random.normal(0, 0.003) + self.log_pos[i] for i in range(2)]
                         [np.random.normal(0.005 * flow[i], 0.005) + self.log_pos[i] for i in range(2)]][self.group])
        if -1 <= new_pos[0] <= 1 and -1 <= new_pos[1] <= 1:
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

    def social_distance(self, other, active, dif):
        if active:
            if other:
                d = get_norm(dif)
                s = [dif[i] / d for i in range(2)] if d > 0 else (0, 0)
                r = self.parameters["radius"]
                if d < 1.5 * r:
                    self.log_pos = tuple([0.1 * 1.5 * r * s[i] * 0.5 + self.log_pos[i] for i in range(2)])
                    other.log_pos = tuple([0.1 * 1.5 * r * (-s[i]) * 0.5 + other.log_pos[i] for i in range(2)])

    def death(self):
        if self.status == 1:
            self.status = 1 + bernoulli.rvs(self.parameters["death_rate"])

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


class Population(object):

    def __init__(self, builder, size, social_distance=False, groups=1):
        self.size = size
        self.social_distance = social_distance
        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        for k in range(size):
            person_k = Person(builder, k, 0) if k < size/groups else Person(builder, k, 1)
            person_k.set_visited(size)
            if person_k.get_status():
                self.i_people.append(person_k)
            else:
                self.s_people.append(person_k)
        self.people += self.s_people + self.i_people

    def draw(self, pipeline):
        for person in self.people:
            person.draw(pipeline)

    def update(self):
        global c
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
                s_person.social_distance(i_person, active, dif)
                s_person.update_status(i_person, dif)
                if s_person.get_status():
                    self.i_people += [s_person]
                    self.s_people.remove(s_person)
                    print('+1 infectado')
                    break
            for s2_person in self.s_people:
                dif = np.subtract(s_person.get_log_pos(), s2_person.get_log_pos())
                s_person.social_distance(s2_person, active, dif)

            s_person.update_pos()
        print(f'sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}') \
            if not c % 100 else None
        c += 1

    def update_grid_smart(self, mode=3):
        global c
        s_people = self.s_people
        i_people = self.i_people
        d_people = self.d_people
        active = self.social_distance
        p_index = 0
        for person in self.people:
            if (not person.is_visited(p_index)) and (person.get_status() in [0, 1]):
                if person.get_status() == 1:
                    person.update_status()
                    if person.get_status() == 2:
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
                            person.social_distance(person2, active, dif)
                            if person.get_status() == 0 and person2.get_status() == 1:
                                person.update_status(person2, dif)
                                if person.get_status() == 1:
                                    i_people += [person]
                                    s_people.remove(person)
                                    print('+1 infectado')
                                    break
                            elif person.get_status() == 1 and person2.get_status() == 0:
                                person2.update_status(person, dif)
                                if person2.get_status() == 1:
                                    i_people += [person2]
                                    s_people.remove(person2)
                                    print('+1 infectado')
                                    break
                    p2_index += 1
                person.update_pos()
                if person.get_status() == 0:
                    person.set_visited(self.size)
            p_index += 1
        self.s_people = s_people
        self.i_people = i_people
        self.d_people = d_people
        for i_person in self.i_people:
            i_person.set_visited(self.size)
        self.show_data()
        c += 1

    def show_data(self):
        global c
        if not c % 100:
            print(f'sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}')


class Background(object):
    def __init__(self):
        pass

    def draw(self):
        pass


def get_dif(vec1, vec2):
    return [vec1[i] - vec2[i] for i in range(2)]


def get_norm(vec):
    return sum([vec[i] ** 2 for i in range(2)]) ** 0.5


def get_individual_n_grid(n, log_pos):
    return [(log_pos[i]-1/n, log_pos[i]+1/n) for i in range(2)]
