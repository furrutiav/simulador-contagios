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
    window = glfw.create_window(
        width, height, name, None, None)

    if not window:
        glfw.terminate()
        sys.exit()
    glfw.make_context_current(window)

    controller = Controller()

    glfw.set_key_callback(window, controller.on_key)

    pipeline_tx_2d = es.SimpleTextureTransformShaderProgram()
    pipeline_pol_2d = es.SimpleTransformShaderProgram()

    glClearColor(15 / 255, 26 / 255, 43 / 255, 1.0)

    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    b = Builder()
    pop1 = Population(b, size=size1, social_distance=False, groups=2, view_center=(-0.7, 0.5), index=0)
    pop2 = Population(b, size=size2, social_distance=False, groups=2, view_center=(0.7, 0.5), index=1)
    QUAR = QuarantineZone(bound=0.5, view_center=(0, 0.5))
    C = Community(pop1, pop2, QUAR)
    B = Background(C)

    controller.set_community(C)
    controller.set_background(B)

    sleep(1)

    M = Mask()
    while not glfw.window_should_close(window):

        if controller.parameter == 'P':
            controller.plot()

        glfw.poll_events()

        if controller.binary_value:
            C.update()
        else:
            controller.binary_value = not controller.binary_value
            C.update_forward()

        B.update()

        if controller.mask:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glEnable(GL_STENCIL_TEST)
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
            glDepthMask(GL_FALSE)
            glStencilFunc(GL_NEVER, 1, 0xFF)
            glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)

            glStencilMask(0xFF)
            glClear(GL_STENCIL_BUFFER_BIT)

            M.draw(pipeline_pol_2d)

            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
            glDepthMask(GL_TRUE)
            glStencilMask(0x00)
            glStencilFunc(GL_EQUAL, 0, 0xFF)

            C.draw(pipeline_pol_2d)
            B.draw(pipeline_pol_2d, pipeline_tx_2d)

            glStencilFunc(GL_EQUAL, 1, 0xFF)

            glDisable(GL_STENCIL_TEST)

        else:
            controller.mask = True
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            C.draw(pipeline_pol_2d)
            B.draw(pipeline_pol_2d, pipeline_tx_2d)

        glfw.swap_buffers(window)



    glfw.terminate()
