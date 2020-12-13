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
from scipy.stats import bernoulli
from scipy.spatial import distance
from typing import Union

c = 0


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
        "prob_inf": 0.2 / 100,
        "ratio": 0.2,
        "radius": 0.05,
        "death_rate": 0.1 / 100
    }

    def __init__(self, builder):
        self.log_pos = tuple([[np.random.uniform(1, -1) for _ in range(2)],
                              [np.random.normal(0, 0.2) for _ in range(2)]][1])
        self.status = bernoulli.rvs(self.parameters["ratio"])   # self.parameters["status"]["status"]
        self.builder = builder

        node = sg.SceneGraphNode('person')
        node.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1/50)
        ])
        node.childs += [builder.get_graph()[self.status]]

        self.model = node

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update_pos(self):
        global c
        alpha = 0.05
        flow = np.cos(-c*alpha), np.sin(-c*alpha)
        new_pos = tuple([[np.random.normal(0, 0.003) + self.log_pos[i] for i in range(2)],
                         [np.random.normal(0.003*flow[i], 0.005) + self.log_pos[i] for i in range(2)]][1])
        if -1 <= new_pos[0] <= 1 and -1 <= new_pos[1] <= 1:
            self.log_pos = new_pos
        self.model.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1/50)
        ])

    def update_status(self, other=None, dif=0):
        self.death()
        if other:
            self.infect(other, dif)
        self.model.childs = [self.builder.get_graph()[self.status]]

    def infect(self, other, dif):
        if other:
            d = np.linalg.norm(dif)
            r = self.parameters["radius"]
            if d < r:
                self.status = bernoulli.rvs(self.parameters["prob_inf"])

    def social_distance(self, other, active, dif):
        if active:
            if other:
                d = np.linalg.norm(dif)
                s = dif / d if d > 0 else (0, 0)
                r = self.parameters["radius"]
                if d < 1.5*r:
                    self.log_pos = tuple([0.01*s[i] + self.log_pos[i] for i in range(2)])

    def death(self):
        if self.status == 1:
            self.status = 1+bernoulli.rvs(self.parameters["death_rate"])


class Population(object):

    def __init__(self, builder, size, social_distance=False):
        self.social_distance = social_distance
        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        for k in range(size):
            person_k = Person(builder)
            if person_k.status:
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
            if i_person.status-1:
                self.d_people += [i_person]
                self.i_people.remove(i_person)
                print('+1 muerto')

        for s_person in self.s_people:
            active = self.social_distance
            for i_person in self.i_people:
                dif = np.subtract(s_person.log_pos, i_person.log_pos)
                s_person.social_distance(i_person, active, dif)
                s_person.update_status(i_person, dif)
                if s_person.status:
                    self.i_people += [s_person]
                    self.s_people.remove(s_person)
                    print('+1 infectado')
                    break
            for s2_person in self.s_people:
                dif = np.subtract(s_person.log_pos, s2_person.log_pos)
                s_person.social_distance(s2_person, active, dif)

            s_person.update_pos()
        print(f'sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}') \
            if not c % 100 else None
        c += 1


class Background(object):
    def __init__(self):
        pass

    def draw(self):
        pass
