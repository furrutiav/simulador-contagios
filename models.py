"""
F. Urrutia V., CC3501, 2020-1
-----------> MODELS <-----------
Modelos:
"""

from libs import basic_shapes as bs, transformations as tr, easy_shaders as es, scene_graph as sg
import numpy as np
from OpenGL.GL import *
import random as rd
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
            node = sg.SceneGraphNode(f'node_{i}')
            node.childs += [self._gpu_models[i]]

            self._graph += [node]

    def get_graph(self):
        return self._graph


class Person(object):
    parameters = {
        "labels": ["sano", "infectado", "muerto"],
    }

    def __init__(self, builder):

        self.log_pos = 0, 0
        self.label = "sano"

        node = sg.SceneGraphNode('person')
        node.transform = tr.identity()
        node.childs += [builder.get_graph()[0]]

        self.model = node

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')


class Background(object):
    def __init__(self):
        pass

    def draw(self):
        pass
