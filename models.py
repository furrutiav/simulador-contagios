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
import json

# load virus
virus = open('virus.json')
data_virus = json.load(virus)[0]
# init time
time = 0
pause = False

color_dict = {'g': (0, 1, 0), 'r': (1, 0, 0), 'grey': (0.4, 0.4, 0.4),
              'b': (0, 0, 1), 'w': (1, 1, 1), 'y': (1, 1, 0), 'cian': (0, 1, 1)}

width, height = int(1920 * 0.8), int(1080 * 0.8)
aspect_ratio = width / height
name = 'Simulador Contagios; Autor: F. Urrutia V.'

size1, size2 = [int(data_virus['Initial_population'] / 2) for _ in range(2)]


class Builder(object):
    def __init__(self):
        self._gpu_models = [
            es.toGPUShape(bs.createColorQuad(0, 1, 0)),
            es.toGPUShape(bs.createColorQuad(1, 0, 0)),
            es.toGPUShape(bs.createColorQuad(0.4, 0.4, 0.4)),
            es.toGPUShape(bs.createColorQuad(0, 0, 1)),
            es.toGPUShape(bs.createColorQuad(1, 1, 0)),
            es.toGPUShape(bs.createColorQuad(0, 1, 1))
        ]
        self._graph = []
        for i in range(6):
            node = sg.SceneGraphNode(f'base_node_{i}')
            node.childs += [self._gpu_models[i]]

            self._graph += [node]

    def get_graph(self):
        return self._graph


class Person(object):
    iterations = 50
    parameters = {
        "status": {"sano": 0, "infectado": 1, "muerto": 2, "recuperado": 3, 'false': 4, 'true': 5},
        "prob_inf": data_virus['Contagious_prob'] / iterations,
        "ratio_inf": 0.1,
        "radius": data_virus['Radius'],
        "death_rate": data_virus['Death_rate'] / iterations,
        "days_to_heal": data_virus['Days_to_heal'],
        "ratio_social_distance": 0.5,
        "days_to_quarantine": 1,
        "migration_rate": 1 / iterations

    }

    def __init__(self, builder, index, group=0, population_index=0):
        self.population_index = population_index
        self.social_distance = bernoulli.rvs(self.parameters["ratio_social_distance"])
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

    def update_pos(self, bound=1):
        global time
        flow = [self.circular_flow(2), self.circular_flow(-1)][self.group]
        new_pos = [np.random.normal(0.01 * flow[i], 0.005) + self.log_pos[i] for i in range(2)]
        if -bound < new_pos[0] < bound and -bound < new_pos[1] < bound:
            self.log_pos = new_pos
        self.model.transform = tr.matmul([
            tr.translate(self.log_pos[0], self.log_pos[1], 0),
            tr.uniformScale(1 / 50)
        ])

    def update_status(self, other=None, dif=(0, 0), community=None):
        aux = self.status
        self.death(community=community)
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

    def death(self, community=None):
        global time
        if self.status == 1:
            if community:
                pop = community.get_populations()[self.population_index]
                if pop.quarantine and time / self.iterations - self.day_zero >= self.parameters["days_to_quarantine"]:
                    quar = community.QUAR
                    pop.quar_move(self, quar)
            if time / self.iterations - self.day_zero >= self.parameters["days_to_heal"]:
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
        self.day_zero = time / self.iterations + 1

    def circular_flow(self, om=1):
        global time
        r = get_norm(self.log_pos)
        theta = get_angle(self.log_pos)
        vx = - om * r * np.sin(theta)
        vy = om * r * np.cos(theta)
        return vx, vy

    def view_social_distance(self, active=True):
        if active:
            self.model.childs = [self.builder.get_graph()[4+self.social_distance]]
        else:
            self.model.childs = [self.builder.get_graph()[self.status]]

    def update_social_distance(self):
        self.social_distance = bernoulli.rvs(self.parameters["ratio_social_distance"])

    def from_move_to(self, pop_out, pop_in, status):

        self.population_index = (self.population_index + 1) % 2

        if status == 'p':
            pop_out.size += -1
            pop_in.size += 1

            pop_out.people.remove(self)
            pop_in.people.append(self)

            if self.status == 0:
                pop_out.s_people.remove(self)
                pop_in.s_people.append(self)
            elif self.status == 1:
                pop_out.i_people.remove(self)
                pop_in.i_people.append(self)
            elif self.status == 2:
                pop_out.d_people.remove(self)
                pop_in.d_people.append(self)
            elif self.status == 3:
                pop_out.r_people.remove(self)
                pop_in.r_people.append(self)

            for person in pop_in.people:
                person.set_visited(pop_in.size)

            for person in pop_out.people:
                person.set_visited(pop_out.size)

        elif status == 'q':
            pop_in.people.append(self)
            pop_out.q_people.append(self)

            self.log_pos = [np.random.normal(0, 0.1) for _ in range(2)]

        pop_out.model.childs.remove(self.model)
        pop_in.model.childs.append(self.model)


class Population(object):

    def __init__(self, builder, size, social_distance=False, quarantine=False, migration=False, groups=1, view_center=(0, 0), index=0):
        self.builder = builder
        self.groups = groups
        self.size = size
        self.social_distance = social_distance
        self.view_center = view_center
        self.quarantine = quarantine
        self.migration = migration

        root = sg.SceneGraphNode('root')
        root.transform = tr.matmul([
            tr.translate(view_center[0], view_center[1], 0),
            tr.uniformScale(0.4),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        root.childs = []

        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        self.r_people = []
        self.q_people = []
        for k in range(size):
            person_k = Person(builder, k, 0, index) if k < size / groups else Person(builder, k, 1, index)
            person_k.set_visited(size)
            if person_k.get_status():
                self.i_people.append(person_k)
            else:
                self.s_people.append(person_k)
            root.childs += [person_k.get_model()]
        self.people += self.s_people + self.i_people

        self.count = [[len(people)] for people in [self.s_people, self.i_people,
                                                   self.d_people, self.r_people]]

        self.model = root

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update_grid_smart(self, mode=3, community=None):
        s_people = self.s_people
        i_people = self.i_people
        d_people = self.d_people
        r_people = self.r_people
        active = self.social_distance
        for p_index, person in enumerate(self.people):
            if not (person.is_visited(p_index) or person in self.q_people) and (person.get_status() in [0, 1, 3]):
                if person.get_status() == 1:
                    person.update_status(community=community)
                    if person.get_status() == 3:
                        r_people += [person]
                        i_people.remove(person)
                        # print('+1 recuperado')
                        break
                    elif person.get_status() == 2:
                        d_people += [person]
                        i_people.remove(person)
                        # print('+1 muerto')
                        break
                person.set_visit(p_index)
                p_log_pos = person.get_log_pos()
                cell = get_individual_n_grid(mode, p_log_pos)
                for p2_index, person2 in enumerate(self.people):
                    if not (person.is_visited(p2_index) or person2 in self.q_people):
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
                                    # print('+1 infectado')
                                    break
                            elif person.get_status() == 1 and person2.get_status() == 0:
                                person2.update_status(person, dif)
                                if person2.get_status() == 1:
                                    person2.set_day_zero()
                                    i_people += [person2]
                                    s_people.remove(person2)
                                    # print('+1 infectado')
                                    break
                person.update_pos()
                if person.get_status() in [0, 3]:
                    person.set_visited(self.size)
        self.s_people = s_people
        self.i_people = i_people
        self.d_people = d_people
        self.r_people = r_people
        for i_person in self.i_people:
            i_person.set_visited(self.size)
        for index, people in enumerate([self.s_people, self.i_people, self.d_people, self.r_people]):
            self.count[index].append(len(people))

    def update(self, community):
        global pause
        if self.migration and bernoulli.rvs(Person.parameters['migration_rate']):
            pause = True
            pop_ = list(set(community.get_populations())-{self})[0]
            self.rand_move(pop_)
        if not pause:
            self.update_grid_smart(community=community)

    def show_data(self, label=''):
        global time
        if not time % Person.iterations:
            print(f'[{label}] sanos: {len(self.s_people)}, infectados: {len(self.i_people)}, muertos: {len(self.d_people)}, '
                  f'recuperados: {len(self.r_people)}')

    def update_forward(self):
        for _ in range(Person.iterations):
            self.update_grid_smart()

    def restart(self):
        global time
        time = 0
        root = sg.SceneGraphNode('root')
        root.transform = tr.matmul([
            tr.translate(self.view_center[0], self.view_center[1], 0),
            tr.uniformScale(0.4),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        root.childs = []

        self.people = []
        self.s_people = []
        self.i_people = []
        self.d_people = []
        self.r_people = []
        self.q_people = []
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

    def view_social_distance(self, active=True):
        for person in self.people:
            person.view_social_distance(active)

    def update_social_distance(self, status='+'):
        for person in self.people:
            if person.social_distance == 0 and status == '+':
                person.update_social_distance()
            elif person.social_distance == 1 and status == '-':
                person.update_social_distance()

    def move_to(self, person, pop, status):
        person.from_move_to(self, pop, status)

    def rand_move(self, pop):
        list_choice = list(set(self.people) - set(self.q_people))
        person = rd.choice(list_choice)
        self.move_to(person, pop, 'p')

    def rand_quar_move(self, quar):
        list_choice = list(set(self.i_people)-set(self.q_people))
        if list_choice:
            person = rd.choice(list_choice)
            self.move_to(person, quar, 'q')

    def quar_move(self, person, quar):
        self.move_to(person, quar, 'q')


class Community(object):
    def __init__(self, pop1, pop2, quar):
        self.pop1 = pop1
        self.pop2 = pop2
        self.QUAR = quar

    def update(self):
        global time, pause
        for _, pop in enumerate([self.pop1, self.pop2]):
            pop.update(self)
        self.QUAR.update()

        if pause:
            pause = not pause

        time += 1

    def update_forward(self):
        global time
        for _, pop in enumerate([self.pop1, self.pop2]):
            pop.update_forward()
        time += Person.iterations

    def draw(self, pipeline):
        for _, pop in enumerate([self.pop1, self.pop2]):
            pop.draw(pipeline)

        self.QUAR.draw(pipeline)

    def get_populations(self):
        return [self.pop1, self.pop2]


class QuarantineZone(object):
    def __init__(self, bound, view_center=(0, 0)):
        self.view_center = view_center
        self.bound = bound

        root = sg.SceneGraphNode('root')
        root.transform = tr.matmul([
            tr.translate(view_center[0], view_center[1], 0),
            tr.uniformScale(0.4),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        root.childs = []

        self.people = []

        self.model = root

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')

    def update(self):
        for person in self.people:
            if person.get_status() in [1, 3]:
                person.update_pos(self.bound)
                if person.get_status() == 1:
                    person.update_status()


class Background(object):
    def __init__(self, community):
        self.community = community
        self.select = 0

        self.populations = community.get_populations()
        self.QUAR = community.QUAR

        back_gpu = es.toGPUShape(bs.createTextureQuad('img/back.png'), GL_REPEAT,
                                       GL_NEAREST)

        square_gpu = es.toGPUShape(bs.createColorQuad(0.05, 0.07, 0.11))
        bound_gpu = es.toGPUShape(bs.createColorQuad(1, 1, 1))

        back = sg.SceneGraphNode('back')
        back.transform = tr.uniformScale(2)
        back.childs += [back_gpu]

        pop1 = self.populations[0]
        view_center1 = pop1.view_center[0], pop1.view_center[1], 0

        bound = sg.SceneGraphNode('bound')
        bound.transform = tr.matmul([
            apply_tuple(tr.translate)(view_center1),
            tr.uniformScale(0.81),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        bound.childs += [bound_gpu]

        square1 = sg.SceneGraphNode('square1')
        square1.transform = tr.matmul([
            apply_tuple(tr.translate)(view_center1),
            tr.uniformScale(0.8),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        square1.childs += [square_gpu]

        pop2 = self.populations[1]
        view_center2 = pop2.view_center[0], pop2.view_center[1], 0

        square2 = sg.SceneGraphNode('square2')
        square2.transform = tr.matmul([
            apply_tuple(tr.translate)(view_center2),
            tr.uniformScale(0.8),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        square2.childs += [square_gpu]

        view_center3 = self.QUAR.view_center[0], self.QUAR.view_center[1], 0

        square3 = sg.SceneGraphNode('square2')
        square3.transform = tr.matmul([
            apply_tuple(tr.translate)(view_center3),
            tr.uniformScale(0.8 * self.QUAR.bound),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        square3.childs += [square_gpu]

        squares = sg.SceneGraphNode('squares')
        squares.childs += [square1, square2, square3, bound]

        self.bound = bound
        self.bars = []
        self.buttons = []
        self.graphs = []

        self.model = squares

        self.model_tx = back

        static = sg.SceneGraphNode('static')

        self.model_static = static

        x_info = -0.29
        y_info = 0.33
        for i, c in enumerate(list(color_dict.keys())[:4]):
            self.set_percent_bar(color=c, center=(x_info, (2-i) * 0.2 + y_info))

        self.set_percent_bar(color='w', center=(0, 0.88))

        x_settings = 0.35
        y_settings = -0.255
        for i, c in enumerate(['r', 'y', 'grey', 'b']):
            self.set_percent_bar(color=c, center=(x_settings, y_settings-0.2*i))

        x_gob = 0.29
        y_gob = 0.75

        self.set_button(active=0, center=(x_gob, y_gob))

        self.set_percent_bar(color='cian', center=(x_gob, y_gob - 0.1))

        self.set_button(color='r', active=0, center=(x_gob, y_gob-0.2))

        self.set_percent_bar(color='r', center=(x_gob, y_gob - 0.3))

        self.set_button(color='y', center=(x_gob, y_gob - 0.4))

        self.set_percent_bar(color='y', center=(x_gob, y_gob - 0.5))

        self.set_graph(size=(1.0, 0.4), center=(-0.4, -0.5))

        self.graphs[0].plot([], 'g')
        self.graphs[0].plot([], 'r')
        self.graphs[0].plot([], 'grey')
        self.graphs[0].plot([], 'b')

    def draw(self, pipeline, pipeline_tx, status='dynamic'):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')
        if status == 'static':
            sg.drawSceneGraphNode(self.model_static, pipeline, transformName='transform')
        glUseProgram(pipeline_tx.shaderProgram)
        sg.drawSceneGraphNode(self.model_tx, pipeline_tx, transformName='transform')

    def set_percent_bar(self, value=0, size=(0.5, 0.05), center=(0, 0), color='g'):
        pB = PercentBar(value, size, center, color)
        self.bars.append(pB)
        self.model.childs += [pB.get()]

    def set_button(self, active=0, size=(0.05, 0.05), center=(0, 0), color='cian'):
        b = Button(active, size, center, color)
        self.buttons.append(b)
        self.model.childs += [b.get()]

    def update(self):
        global pause
        pop = self.populations[self.select]
        for i, b in enumerate(self.bars[:4]):
            b.set(pop.count[i][-1] / pop.size)

        ite = Person.iterations
        self.bars[4].set((time % ite)/ite)

        self.bars[5].set(Person.parameters['prob_inf'] * ite)

        self.bars[6].set(Person.parameters['radius']/0.2)

        self.bars[7].set(Person.parameters['death_rate'] * ite)

        self.bars[8].set(Person.parameters['days_to_heal']/14)

        self.bars[9].set(Person.parameters['ratio_social_distance'])

        self.bars[10].set(Person.parameters['days_to_quarantine']/14)

        self.bars[11].set(Person.parameters['migration_rate'] * ite)

        pop.show_data(self.select+1)

    def set_select(self, value):
        self.select = value
        pop = self.populations[self.select]
        view_center = pop.view_center[0], pop.view_center[1], 0
        self.bound.transform = tr.matmul([
            apply_tuple(tr.translate)(view_center),
            tr.uniformScale(0.81),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])

    def set_graph(self, size=(0.5, 0.3), center=(-0.5, -0.5)):
        g = GraphMath(size, center)
        self.graphs.append(g)
        self.model_static.childs += [g.get()]


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
            apply_tuple(tr.scale)(size),
            tr.scale(1 / aspect_ratio, 1, 1)
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


class Button(object):
    def __init__(self, active, size, center, color):
        in_button_gpu = es.toGPUShape(apply_tuple(bs.createColorQuad)(color_dict[color]))
        out_button_gpu = es.toGPUShape(bs.createColorQuad(0.05, 0.07, 0.11))

        out_button = sg.SceneGraphNode('out_button')
        out_button.childs += [out_button_gpu]

        in_button = sg.SceneGraphNode('in_button')
        in_button.transform = tr.matmul([
            tr.scale(active, 1, 1)
        ])
        in_button.childs += [in_button_gpu]

        center = center[0], center[1], 0
        size = size[0], size[1], 1

        button = sg.SceneGraphNode('button')
        button.transform = tr.matmul([
            apply_tuple(tr.translate)(center),
            apply_tuple(tr.scale)(size),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        button.childs += [in_button, out_button]

        self.in_button = in_button
        self.model = button

    def set(self, active):
        self.in_button.transform = tr.matmul([
            tr.scale(active, 1, 1)
        ])

    def get(self):
        return self.model


class GraphMath(object):

    def __init__(self, size, center):
        self.size = size
        self.center = center
        back_gpu = es.toGPUShape(bs.createColorQuad(0.05, 0.07, 0.11))
        line_gpu_dict = {}
        for color in color_dict.keys():
            line_gpu_dict[color] = es.toGPUShape(apply_tuple(bs.createColorQuad)(color_dict[color]))

        back = sg.SceneGraphNode('back')
        back.transform = tr.uniformScale(2)
        back.childs += [back_gpu]

        size = size[0], size[1], 1
        center = center[0], center[1], 0

        graph = sg.SceneGraphNode('graph')
        graph.transform = tr.matmul([
            apply_tuple(tr.translate)(center),
            apply_tuple(tr.scale)(size),
            tr.scale(1 / aspect_ratio, 1, 1)
        ])
        graph.childs += [back]

        self.line_gpu_dict = line_gpu_dict

        self.plots = []
        self.model = graph

    def get(self):
        return self.model

    def plot(self, x, color='g'):
        plot = sg.SceneGraphNode('plot')
        n = len(x)

        alpha = 2 / (n-1)
        for i in range(n-1):
            xi = x[i] / 50 - 1
            xi1 = x[i + 1] / 50 - 1
            theta = np.arctan2(xi1-xi, alpha)
            lx = get_norm(get_dif((0, xi), (alpha, xi1)))
            subline = sg.SceneGraphNode(f'subline_{i}')
            subline.transform = tr.matmul([
                tr.translate(i*alpha - 1, xi, 0),
                tr.rotationZ(theta),
                tr.translate(lx / 2, 0, 0),
                tr.scale(lx, 0.005, 1)
            ])
            subline.childs += [self.line_gpu_dict[color]]
            plot.childs += [subline]

        self.plots.append(plot)
        self.model.childs = [plot] + self.model.childs

    def update_plot(self, plot, x, color='g', pop_size=100):
        n = len(x)
        alpha = 2 / (n - 1)
        plot.childs = []
        for i in range(n - 2):
            xi = 2 * x[i] / pop_size - 1
            xi1 = 2 * x[i + 1] / pop_size - 1
            theta = np.arctan2(xi1-xi, alpha)
            lx = get_norm(get_dif((0, xi), (alpha, xi1)))
            subline = sg.SceneGraphNode(f'subline_{i}')
            subline.transform = tr.matmul([
                tr.translate(i*alpha - 1, xi, 0),
                tr.rotationZ(theta),
                tr.translate(lx / 2, 0, 0),
                tr.scale(lx, 0.008, 1)
            ])
            subline.childs += [self.line_gpu_dict[color]]
            plot.childs += [subline]


class Mask(object):
    def __init__(self):
        gpu = es.toGPUShape(bs.createColorQuad(1, 1, 1))

        square = sg.SceneGraphNode('square')
        square.transform = tr.matmul([
            tr.translate(-0.4, -0.5, 0),
            tr.scale(1.0, 0.4, 1),
            tr.uniformScale(2),
            tr.scale(1/aspect_ratio, 1, 1)
        ])
        square.childs += [gpu]

        mask = sg.SceneGraphNode('mask')
        mask.childs += [square]

        self.model = mask

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, transformName='transform')


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
