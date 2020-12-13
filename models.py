"""
F. Urrutia V., CC3501, 2020-1
-----------> MODELS <-----------
Modelos:
"""

from libs import basic_shapes as bs, transformations as tr, easy_shaders as es, scene_graph as sg
import numpy as np
from OpenGL.GL import *
import random as rd
from scipy.stats import bernoulli
from scipy.spatial import distance
from typing import Union


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
        "prob_inf": 0.5,
        "ratio": 0.1,
        "radius": 0.1
    }

    def __init__(self, builder):
        self.log_pos = np.random.uniform(1, -1), np.random.uniform(1, -1)
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
        self.log_pos = tuple([np.random.normal(0, 0.003) + self.log_pos[i] for i in range(2)])
        self.model.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1/50)
        ])

    def update_status(self, other=None, active=False):
        self.social_distance(other, active)
        self.model.childs = [self.builder.get_graph()[self.status]]

    def social_distance(self, other, active):
        if not active:
            if other:
                d = distance.euclidean(self.log_pos, other.log_pos)
                if d < self.parameters["radius"]:
                    self.status = bernoulli.rvs(self.parameters["prob_inf"])


class Population(object):

    def __init__(self, builder, size):
        self.people = []
        self.s_people = []
        self.i_people = []
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
        for i_person in self.i_people:
            i_person.update_pos()

        for s_person in self.s_people:
            for i_person in self.i_people:
                s_person.update_status(i_person)
                if s_person.status:
                    self.i_people += [s_person]
                    self.s_people.remove(s_person)
                    break
            s_person.update_pos()


class Background(object):
    def __init__(self):
        pass

    def draw(self):
        pass
