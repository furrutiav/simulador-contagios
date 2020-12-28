"""
F. Urrutia V., CC3501, 2020-1
-----------> VIEW <-----------
         Visualización
"""
import glfw
import sys
from models import *
from controller import Controller
from time import sleep

if __name__ == '__main__':
    if not glfw.init():
        sys.exit()
    # second_monitor = glfw.get_monitors()[1]
    window = glfw.create_window(
        width, height, 'Simulador Contagios; Autor: F. Urrutia V.', None, None)

    if not window:
        glfw.terminate()
        sys.exit()
    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)
    glfw.set_scroll_callback(window, controller.on_scroll)

    pipeline_tx_2d = es.SimpleTextureTransformShaderProgram()
    pipeline_pol_2d = es.SimpleTransformShaderProgram()

    glClearColor(15 / 255, 26 / 255, 43 / 255, 1.0)

    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    b = Builder()
    pop1 = Population(b, size=100, social_distance=False, groups=2, view_center=(0.5, 0.5))
    pop2 = Population(b, size=100, social_distance=False, groups=2, view_center=(0.5, -0.5))
    C = Community(pop1, pop2)
    B = Background(pop1)

    controller.set_population(pop1)

    sleep(1)

    while not glfw.window_should_close(window):

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if controller.binary_value:
            C.update()
            B.update()

        else:
            controller.binary_value = not controller.binary_value
            C.update_forward()

        C.draw(pipeline_pol_2d)
        B.draw(pipeline_pol_2d)

        glfw.swap_buffers(window)

    glfw.terminate()
