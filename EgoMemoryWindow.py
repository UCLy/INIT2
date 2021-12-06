import pyglet
from pyglet.gl import *
from OsoyooCar import OsoyooCar
from WifiInterface import WifiInterface
import json
from Phenomenon import Phenomenon
import math
from pyglet import shapes
from pyglet import clock

import threading
import time

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


class EgoMemoryWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.zoom_level = 1

        self.robot = OsoyooCar(self.batch)
        self.wifiInterface = WifiInterface()

        self.phenomena = []
        # self.origin = shapes.Circle(0, 0, 20, color=(150, 150, 225))
        self.origin = shapes.Rectangle(0, 0, 60, 40, color=(150, 150, 225))
        self.origin.anchor_position = 30, 20


        self.environment_matrix = (GLfloat * 16)(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)

        self.outcome = "{}"
        #glLoadIdentity()
        #glTranslatef(150, 0, 0)
        #glGetFloatv(GL_MODELVIEW_MATRIX, self.envMat)  # The only way i found to set envMat to identity

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
    
        # The transformations are stacked, and applied backward to the vertices

        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        # glRotatef(90, 0.0, 0.0, 1.0)

        # Draw the robot and the phenomena
        self.batch.draw()

        # Stack the environment's displacement and draw the origin just to check
        glMultMatrixf(self.environment_matrix)
        self.origin.draw()  # Draw the origin of the robot

    def on_resize(self, width, height):
        # Display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired from https://www.py4u.net/discuss/148957
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def on_text(self, text):
        print("Send action: ", text)
        outcome_string = self.wifiInterface.enact(text)
        print(outcome_string)
        outcome = json.loads(outcome_string)

        self.windowRefresh(text, outcome)

    def windowRefresh(self, text, outcome):
        # Update the model from the outcome
        translation = [0, 0]
        rotation = 0
        if text == "1":
            rotation = 45
        if text == "2":
            translation[0] = 180
        if text == "3":
            rotation = -45
        if text == "8":
            translation[0] = -180

        if 'head_angle' in outcome:
            head_angle = outcome['head_angle']
            print("Head angle %i" % head_angle)
            self.robot.rotate_head(head_angle)
        if 'yaw' in outcome:
            rotation = outcome['yaw']
        if text == "-" or text == "*":
            if 'echo_distance' in outcome:
                echo_distance = outcome['echo_distance']
                print("Echo distance %i" % echo_distance)
                x = self.robot.head_x + math.cos(math.radians(head_angle)) * echo_distance
                y = self.robot.head_y + math.sin(math.radians(head_angle)) * echo_distance
                obstacle = Phenomenon(x, y, self.batch)
                self.phenomena.append(obstacle)

        for p in self.phenomena:
            p.translate(translation)
            p.rotate(-rotation)

        glLoadIdentity()
        glTranslatef(translation[0], translation[1], 0)
        glRotatef(-rotation, 0, 0, 1.0)
        glMultMatrixf(self.environment_matrix)
        glGetFloatv(GL_MODELVIEW_MATRIX, self.environment_matrix)

    # Boucle en arrière plan pour demander régulièrement des informations au robot
    def actionLoop(self, frequence):
        def loop(obj: EgoMemoryWindow):
            while True:
                time.sleep(frequence)
                print("Data requests")
                obj.outcome = obj.wifiInterface.enact('$')
                # obj.windowRefresh('$', json.loads(outcome))

        thread = threading.Thread(target=loop, args=[self])
        thread.start()

    # Boucle executer par pyglet pour utiliser les fonction de actionLoop
    def actionLoopInterprete(self, dt):
        if self.outcome != "{}":
            print(self.outcome)
            self.windowRefresh('$', json.loads(self.outcome))
            self.outcome = "{}"


if __name__ == "__main__":
    em_window = EgoMemoryWindow()
    em_window.actionLoop(10)
    clock.schedule_interval(em_window.actionLoopInterprete, 5)
    pyglet.app.run()