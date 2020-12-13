"""
F. Urrutia V., CC3501, 2020-1
-----------> VIEW <-----------
         Visualización
"""
import glfw
import sys
import imgui
from models import *
from controller import Controller


if __name__ == '__main__':
    if not glfw.init():
        sys.exit()

    width, height = 900, 900
    # second_monitor = glfw.get_monitors()[1]
    window = glfw.create_window(
        width, height, 'Simulador Contagios; Autor: F. Urrutia V.', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)

    pipeline_tx_2d = es.SimpleTextureTransformShaderProgram()
    pipeline_pol_2d = es.SimpleTransformShaderProgram()

    glClearColor(15 / 255, 33 / 255, 26 / 105, 1.0)

    # glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    b = Builder()
    p = Population(b, 100)
    controller.set_population(p)
    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        p.update()

        p.draw(pipeline_pol_2d)

        glfw.swap_buffers(window)

    glfw.terminate()
