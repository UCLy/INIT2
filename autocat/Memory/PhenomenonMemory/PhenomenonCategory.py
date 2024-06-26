from pyrr import Vector3
import numpy as np
from .. import CELL_RADIUS
from ..EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ...Utils import azimuth_to_quaternion
from .Affordance import MIDDLE_COLOR_INDEX, COLOR_DISTANCE
from . import PHENOMENON_RECOGNIZABLE_CONFIDENCE

point_distance = CELL_RADIUS


def oval_shape(x_radius, y_radius, azimuth_quaternion):
    """Compute the list of points drawing the oval shape"""
    segment = x_radius - y_radius

    # Create points on the right half-circle
    theta = np.linspace(np.pi / 2, -np.pi / 2, int(np.pi * y_radius / point_distance), endpoint=False)
    x = y_radius * np.cos(theta)
    y = y_radius * np.sin(theta)
    z = np.zeros(len(x))
    right_circle = np.column_stack((x, y, z)) + np.array([segment, 0, 0])

    # Create point on the bottom side
    x = np.linspace(segment, -segment, int(2 * segment / point_distance), endpoint=False)
    y = np.full(len(x), -y_radius)
    z = np.zeros(len(x))
    bottom_side = np.column_stack((x, y, z))

    # Create points on the left half-circle
    theta = np.linspace(3 * np.pi / 2, np.pi / 2, int(np.pi * y_radius / point_distance), endpoint=False)
    x = y_radius * np.cos(theta)
    y = y_radius * np.sin(theta)
    z = np.zeros(len(x))
    left_circle = np.column_stack((x, y, z)) + np.array([-segment, 0, 0])

    # Create point on the top side
    x = np.linspace(-segment, segment, int(2 * segment / point_distance), endpoint=False)
    y = np.full(len(x), y_radius)
    z = np.zeros(len(x))
    top_side = np.column_stack((x, y, z))

    horizontal_oval = np.concatenate((right_circle, bottom_side, left_circle, top_side), axis=0)

    # Rotate by the azimuth
    return np.array([(azimuth_quaternion * Vector3(p)) for p in horizontal_oval])


def rectangular_shape(x_radius, y_radius):
    """Compute the list of points drawing the oval shape"""
    # Top points
    x = np.linspace(-x_radius, x_radius, int(2 * x_radius / point_distance), endpoint=False)
    y = np.full(len(x), y_radius)
    z = np.zeros(len(x))
    top_side = np.column_stack((x, y, z))
    # Left points
    x = np.full(int(2 * y_radius / point_distance), x_radius)
    y = np.linspace(y_radius, -y_radius, int(2 * y_radius / point_distance), endpoint=False)
    z = np.zeros(len(x))
    left_side = np.column_stack((x, y, z))
    # Bottom points
    x = np.linspace(x_radius, -x_radius, int(2 * x_radius / point_distance), endpoint=False)
    y = np.full(len(x), -y_radius)
    z = np.zeros(len(x))
    bottom_side = np.column_stack((x, y, z))
    # Right points
    x = np.full(int(2 * y_radius / point_distance), -x_radius)
    y = np.linspace(-y_radius, y_radius, int(2 * y_radius / point_distance), endpoint=False)
    z = np.zeros(len(x))
    right_side = np.column_stack((x, y, z))
    return np.concatenate((top_side, left_side, bottom_side, right_side), axis=0)


class PhenomenonCategory:
    """Define a kind of phenomenon of oval shape"""
    def __init__(self, experience_type, short_radius, long_radius, azimuth):
        """A new phenomenon type defined by its experience type and its shape."""
        # Primary attributes
        self.experience_type = experience_type
        self.short_radius = short_radius
        self.long_radius = long_radius
        self.azimuth = azimuth
        # Secondary attributes
        self.quaternion = azimuth_to_quaternion(azimuth)
        self.north_east_point = np.array(self.quaternion * Vector3([long_radius, 0, 0]), dtype=int)
        if experience_type == EXPERIENCE_FLOOR:
            self.shape = oval_shape(long_radius, short_radius, self.quaternion)
        else:
            self.shape = rectangular_shape(long_radius, short_radius)

    def polar_egocentric_center(self, affordance):
        """Return the polar egocentric center point of this phenomenon category relative to the affordance"""
        if self.experience_type == EXPERIENCE_FLOOR and affordance.type == EXPERIENCE_FLOOR:
            if affordance.color_index > 0:
                # The color point along the y axis: red positive, purple negative.
                color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])

                if np.dot(affordance.polar_sensor_point, self.north_east_point) < 0:
                    # Robot is North-East TODO check the sign of color_y
                    center_point = -self.north_east_point - self.quaternion * color_y
                    print("Relative center point when Robot is North-East:", center_point)
                else:
                    # Robot is South-West
                    center_point = self.north_east_point + self.quaternion * color_y
                    print("Relative center point when Robot is South-West:", center_point)
                return np.array(center_point, dtype=int)
            else:
                # TODO Estimate the center of the terrain when floor line detected without color
                return None
        else:
            # TODO Estimate the center of the phenomenon from echo
            return np.array([0, 0, 0])

    def is_type_of(self, phenomenon):
        """Return True if the phenomenon has the same experience type and and RECOGNIZE confidence"""
        # Only recognize phenomena that have origin confidence
        return phenomenon.confidence >= PHENOMENON_RECOGNIZABLE_CONFIDENCE and \
               self.experience_type == phenomenon.phenomenon_type
