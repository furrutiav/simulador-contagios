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
    "border": [
        [(-border_radius, border_radius), (-1, 1)],
        [(-1, 1), (-border_radius, border_radius)]
    ]
}


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

    def __init__(self, builder):
        self.log_pos = tuple([[np.random.uniform(1, -1) for _ in range(2)],
                              [np.random.normal(0, 0.2) for _ in range(2)]][0])
        self.status = bernoulli.rvs(self.parameters["ratio"])
        #  self.parameters["status"]["status"]
        self.builder = builder
        self.neighbors_visited = []

        node = sg.SceneGraphNode('person')
        node.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1 / 50)
        ])
        node.childs += [builder.get_graph()[self.status]]

        self.model = node

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update_pos(self):
        global c
        alpha = 0.05
        flow = [(np.cos(-c * alpha), np.sin(-c * alpha)), (-self.log_pos[0], -self.log_pos[1])][1]
        new_pos = tuple([[np.random.normal(0, 0.003) + self.log_pos[i] for i in range(2)],
                         [np.random.normal(0.005 * flow[i], 0.005) + self.log_pos[i] for i in range(2)]][1])
        if -1 <= new_pos[0] <= 1 and -1 <= new_pos[1] <= 1:
            self.log_pos = new_pos
        self.model.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1 / 50)
        ])

    def update_status(self, other=None, dif=(0, 0)):
        self.death()
        if other:
            self.infect(other, dif)
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
                    self.log_pos = tuple([0.1 * 1.5 * r * s[i] + self.log_pos[i] for i in range(2)])

    def death(self):
        if self.status==1:
            self.status = 1 + bernoulli.rvs(self.parameters["death_rate"])

    def get_log_pos(self):
        return self.log_pos

    def get_status(self):
        return self.status

    def set_neighbors_visited(self, size, index):
        self.neighbors_visited = [1 if (i==index and self.status==0) else 0 for i in range(size)]

    def set_visit(self, index_other):
        self.neighbors_visited[index_other] = 1

    def is_visited(self, index_other):
        return self.neighbors_visited[index_other]

    def update_visited(self, index, size):
        self.neighbors_visited = [1 if (i==index and self.status==0) else 0 for i in range(size)]


class Population(object):

    def __init__(self, builder, size, social_distance=False):
        self.size = size
        self.social_distance = social_distance
        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        for k in range(size):
            person_k = Person(builder)
            person_k.set_neighbors_visited(size, k)
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
        c = c % 100

    def update_grid(self):
        global c
        for s_person in self.s_people:
            active = self.social_distance
            s_person_cell = None
            for cell in grid["ternary"]:
                cell_x = cell[0]
                cell_y = cell[1]
                if cell_x[0] <= s_person.log_pos[0] <= cell_x[1] and cell_y[0] <= s_person.log_pos[1] <= cell_y[1]:
                    s_person_cell = cell
                    break

            cell_x = s_person_cell[0]
            cell_y = s_person_cell[1]

            for i_person in self.i_people:
                if cell_x[0] <= i_person.log_pos[0] <= cell_x[1] and cell_y[0] <= i_person.log_pos[1] <= cell_y[1]:
                    dif = get_dif(s_person.log_pos, i_person.log_pos)
                    s_person.social_distance(i_person, active, dif)
                    s_person.update_status(i_person, dif)
                    if s_person.status:
                        self.i_people += [s_person]
                        self.s_people.remove(s_person)
                        print('+1 infectado')
                        break
            for s2_person in self.s_people:
                if cell_x[0] <= s2_person.log_pos[0] <= cell_x[1] and cell_y[0] <= s2_person.log_pos[1] <= \
                        cell_y[1]:
                    dif = get_dif(s_person.log_pos, s2_person.log_pos)
                    s_person.social_distance(s2_person, active, dif)
            s_person.update_pos()
        self.show_data()
        c += 1
        c = c % 100

    def update_grid2(self):
        global c
        p_index = 0
        s_people = self.s_people
        i_people = self.i_people
        d_people = self.d_people
        active = self.social_distance
        for person in self.people:
            person_cell = None
            for cell in grid["ternary"]:
                cell_x = cell[0]
                cell_y = cell[1]
                if cell_x[0] <= person.get_log_pos()[0] <= cell_x[1] \
                        and cell_y[0] <= person.get_log_pos()[1] <= cell_y[1]:
                    person_cell = cell
                    break

            cell_x = person_cell[0]
            cell_y = person_cell[1]

            if person.get_status()==0:
                s_person = person
                s_index = p_index
                p2_index = 0
                for person2 in self.people:
                    if not s_person.is_visited(p2_index):
                        if person2.get_status()==1:
                            i_index = p2_index
                            i_person = person2
                            if cell_x[0] <= i_person.get_log_pos()[0] <= cell_x[1] \
                                    and cell_y[0] <= i_person.get_log_pos()[1] <= cell_y[1]:
                                dif = get_dif(s_person.get_log_pos(), i_person.get_log_pos())
                                s_person.social_distance(i_person, active, dif)
                                s_person.update_status(i_person, dif)
                                if s_person.status:
                                    i_people += [s_person]
                                    s_people.remove(s_person)
                                    print('+1 infectado')
                                    break
                            if not i_person.is_visited(i_index):
                                i_person.set_visit(i_index)
                                i_person.update_pos()
                                i_person.update_status()
                                if i_person.get_status() - 1:
                                    d_people += [i_person]
                                    i_people.remove(i_person)
                                    print('+1 muerto')
                            s_person.set_visit(i_index)
                            i_person.set_visit(s_index)
                        if person2.get_status()==0:
                            s2_index = p2_index
                            s2_person = person2
                            s_person.set_visit(s2_index)
                            s2_person.set_visit(s_index)
                            if cell_x[0] <= s2_person.get_log_pos()[0] <= cell_x[1] \
                                    and cell_y[0] <= s2_person.get_log_pos()[1] <= cell_y[1]:
                                dif = get_dif(s_person.get_log_pos(), s2_person.get_log_pos())
                                s_person.social_distance(s2_person, active, dif)
                                s2_person.social_distance(s_person, active, [-dif[0], -dif[1]])
                    p2_index += 1
                s_person.update_pos()
                person.update_visited(p_index, self.size)
            elif person.get_status()==1:
                i_index = p_index
                i_person = person
                if not i_person.is_visited(i_index):
                    i_person.set_visit(i_index)
                    i_person.update_pos()
                    i_person.update_status()
                    if i_person.get_status() - 1:
                        d_people += [i_person]
                        i_people.remove(i_person)
                        print('+1 muerto')
            p_index += 1
        self.s_people = s_people
        self.i_people = i_people
        self.d_people = d_people
        for i_person in i_people:
            i_person.update_visited(p_index, self.size)
        self.show_data()
        c += 1
        c = c % 100

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
