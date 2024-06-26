import math
import numpy as np
from pyrr import matrix44, Vector3
from ..EgocentricMemory.Experience import EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO, \
    EXPERIENCE_FLOOR
from ...Utils import assert_almost_equal_angles, quaternion_to_direction_rad

MAX_SIMILAR_DISTANCE = 300    # (mm) Max distance within which affordances are similar
MAX_SIMILAR_DIRECTION = 15    # (degrees) Max angle within which affordances are similar
MIN_OPPOSITE_DIRECTION = 135  # (degrees) Min angle to tell affordances are in opposite directions
COLOR_DISTANCE = 50           # (mm) The distance between patches of colors. On A4 paper: 40mm. On A3 paper: 50mm
MIDDLE_COLOR_INDEX = 4        # (color index) The index of the middle color (green)


class Affordance:
    """An affordance is an experience localized relative to a phenomenon"""
    def __init__(self, point, experience_type, clock, color_index, quaternion, polar_sensor_point):
        """Position should be integer to facilitate search"""
        self.point = point  # The position of this affordance relative to a phenomenon
        self.type = experience_type
        self.clock = clock
        self.color_index = color_index
        self.quaternion = quaternion  # The absolute direction of this affordance
        self.polar_sensor_point = polar_sensor_point  # The position of the sensor relative to the affordance

    def __str__(self):
        return f"(Point:({self.point[0]},{self.point[1]}) ,clock:{self.clock}, type:{self.type}, " \
               f"color_index:{self.color_index})"

    def absolute_direction_rad(self):
        """Return the absolute direction of this affordance"""
        return quaternion_to_direction_rad(self.quaternion)

    def is_similar_to(self, other_affordance):
        """Return True if the the two interactions are similar"""

        # Echo affordances
        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # Similar if they have similar point and their experience have similar absolute direction
            if other_affordance.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
                if math.dist(self.point, other_affordance.point) < MAX_SIMILAR_DISTANCE:
                    if assert_almost_equal_angles(self.absolute_direction_rad(),
                                                  other_affordance.absolute_direction_rad(),
                                                  MAX_SIMILAR_DIRECTION):
                        # print("Near affordance: point 1:", self.point, ", point 2:", other_affordance.point,
                        #       ", direction 1: ", round(math.degrees(self.experience.absolute_direction_rad)),
                        #       "°, direction 2: ", round(math.degrees(other_affordance.experience.absolute_direction_rad)), "°")
                        return True
        # Floor affordances colored
        if self.type == EXPERIENCE_FLOOR and self.color_index > 0:
            if other_affordance.type == EXPERIENCE_FLOOR and self.color_index > 0:
                print("Similar Floor affordances")
                return True

        return False

    def is_opposite_to(self, other_affordance):
        """Affordances are opposite to if their absolute directions are not close to each other"""
        if not assert_almost_equal_angles(self.absolute_direction_rad(),
                                          other_affordance.absolute_direction_rad(),
                                          MIN_OPPOSITE_DIRECTION):
            print("Opposite affordance: direction 1:", round(math.degrees(self.absolute_direction_rad())),
                  "°, direction 2: ", round(math.degrees(other_affordance.absolute_direction_rad())), "°")
            return True
        return False

    def is_clockwise_from(self, other_affordance):
        """this affordance is in clockwise direction (within pi/4) from the other affordance in argument"""
        new_affordance_angle = self.absolute_direction_rad() % (2 * math.pi)
        origin_angle = other_affordance.absolute_direction_rad() % (2 * math.pi)
        if origin_angle > new_affordance_angle:
            if (origin_angle - new_affordance_angle) <= math.pi / 4:  # Clockwise and within pi/4
                print("Clockwise: new direction:", round(math.degrees(new_affordance_angle)),
                      "°, from origin direction: ", round(math.degrees(origin_angle)), "°")
                return True
        else:
            if (new_affordance_angle - origin_angle) >= 7 * math.pi / 4:  # 2pi-pi/4 = 315°
                print("Clockwise: new direction:", round(math.degrees(new_affordance_angle)),
                      "°, from origin direction: ", round(math.degrees(origin_angle)), "°")
                return True
        return False

    def sensor_triangle(self):
        """Return the set of points to display the echolocalization cone"""
        points = None
        if self.type in [EXPERIENCE_ALIGNED_ECHO, EXPERIENCE_CENTRAL_ECHO]:
            # The position of the head from the position of the affordance
            p1 = self.polar_sensor_point
            # The direction of p2 is orthogonal to the direction of the sensor
            orthogonal_rotation = matrix44.create_from_z_rotation(math.pi/2)
            p2 = matrix44.apply_to_vector(orthogonal_rotation, p1) * 0.4
            # p3 is opposite to p2 from the position of the affordance
            p3 = p2 * -0.8
            # Add the position of the affordance to the position of the triangle
            points = [p1, p2, p3] + self.point
        return points

    # def polar_green_point(self):
    #     """Return the point of the expected green patch, polar-centric relative to this affordance"""
    #     # The color point along the y axis: red positive, purple negative.
    #     color_y = Vector3([0, (MIDDLE_COLOR_INDEX - self.color_index) * COLOR_DISTANCE, 0])
    #     return np.array(self.polar_sensor_point - self.quaternion * color_y, dtype=int)

    def save(self):
        """Return a cloned affordance for memory snapshot"""
        return Affordance(self.point.copy(), self.type, self.clock, self.color_index, self.quaternion.copy(),
                          self.polar_sensor_point.copy())
