import math
import numpy as np
from pyrr import Vector3, Quaternion
from . import PHENOMENON_RECOGNIZABLE_CONFIDENCE, PHENOMENON_RECOGNIZED_CONFIDENCE, TERRAIN_ORIGIN_CONFIDENCE, \
    PHENOMENON_ENCLOSED_CONFIDENCE
from .Phenomenon import Phenomenon
from .Affordance import Affordance, MIDDLE_COLOR_INDEX, COLOR_DISTANCE
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_PLACE, EXPERIENCE_FLOOR
from ...Utils import short_angle


# TERRAIN_EXPERIENCE_TYPES = [EXPERIENCE_FLOOR]  # EXPERIENCE_PLACE


class PhenomenonTerrain(Phenomenon):
    """A hypothetical phenomenon related to floor detection"""
    def __init__(self, affordance):
        super().__init__(affordance)
        self.phenomenon_type = EXPERIENCE_FLOOR
        self.interpolation_types = [EXPERIENCE_FLOOR]

        # If the affordance is color floor then use it as absolute origin
        if affordance.type == EXPERIENCE_FLOOR and affordance.color_index > 0:
            self.absolute_affordance_key = 0
            self.last_origin_clock = affordance.clock
            self.origin_direction_quaternion = affordance.quaternion.copy()
            self.confidence = TERRAIN_ORIGIN_CONFIDENCE
            # create_phenomenon() will call recognize()

    def update(self, affordance: Affordance):
        """Test if the affordance is within the acceptable delta from the position of the phenomenon,
        if yes, add the affordance to the phenomenon, and return the robot's position correction."""
        # Check if the affordance is acceptable for this phenomenon type
        if affordance.type == EXPERIENCE_FLOOR:
            # Add the affordance
            affordance.point = affordance.point.astype(int) - self.point.astype(int)
            self.affordance_id += 1
            self.affordances[self.affordance_id] = affordance
            position_correction = np.array([0, 0, 0], dtype=int)

            # If color
            if affordance.color_index > 0:
                # If the phenomenon does not have an absolute origin yet then this affordance becomes the absolute
                if self.confidence < TERRAIN_ORIGIN_CONFIDENCE:
                    # This experience becomes the phenomenon's absolute origin
                    self.absolute_affordance_key = self.affordance_id
                    # The phenomenon's direction is the absolute direction of this affordance
                    self.origin_direction_quaternion = affordance.quaternion.copy()
                    self.last_origin_clock = affordance.clock
                    self.confidence = TERRAIN_ORIGIN_CONFIDENCE
                    # The terrain position is moved to the green sensor position relative to this FLOOR affordance
                    # (Assume the pattern of the color patch)
                    # The terrain origin remains at the terrain position
                    terrain_offset = self.vector_toward_origin(affordance)
                    self.point += terrain_offset
                    for a in self.affordances.values():
                        a.point -= terrain_offset
                elif abs(short_angle(affordance.quaternion, self.origin_direction_quaternion)) < math.pi / 2 \
                        or self.confidence >= PHENOMENON_RECOGNIZABLE_CONFIDENCE:
                    # If this affordance is in the direction of the origin or terrain is recognized
                    position_correction = self.vector_toward_origin(affordance)
                    # Prediction error is opposite of the position_correction projected along the color direction
                    self.origin_prediction_error[affordance.clock] = np.dot(-position_correction,
                                                                     affordance.quaternion * Vector3([0., 1., 0.]))
                    # Correct the position of the affordances since last time the robot visited the absolute origin
                    self.enclose(position_correction, affordance.clock)
                    # Increase confidence if not consecutive origin affordances
                    # if affordance.clock - self.last_origin_clock > 5:
                    self.confidence = max(PHENOMENON_RECOGNIZABLE_CONFIDENCE, self.confidence)
            # Black line: Compute the position correction based on the nearest point in the terrain shape
            # TODO use the point on the trajectory rather than the closest point
            elif self.confidence >= PHENOMENON_RECOGNIZED_CONFIDENCE:  # PHENOMENON_CLOSED_CONFIDENCE
                distances = np.linalg.norm(self.shape - affordance.point, axis=1)
                closest_point = self.shape[np.argmin(distances)]
                position_correction = np.array(affordance.point - closest_point, dtype=int)
                print("Nearest shape point", closest_point, "Position correction", position_correction)
                affordance.point -= position_correction
            elif self.confidence >= PHENOMENON_ENCLOSED_CONFIDENCE:
                # Recenter the terrain
                # self.move_origin(self.shape.mean(axis=0).astype(int))
                self.prune(affordance)
                self.reshape()

            # if the phenomenon is not recognized, recompute the shape
            # if self.confidence == PHENOMENON_ENCLOSED_CONFIDENCE:
            #     # self.interpolate()
            #     self.reshape()

            return 0  # - position_correction  # TODO remove the minus sign
        # Affordances that do not belong to this phenomenon must return None
        return None

    def try_to_enclose(self):  # TODO improve and use it for automatic enclosure
        """If the area is big enough, increase confidence and interpolate the closed shape"""
        if self.confidence < PHENOMENON_ENCLOSED_CONFIDENCE:
            vertices = [a.point[0:2] for a in self.affordances.values() if a.type in self.interpolation_types]
            if len(vertices) > 2:
                vertices.append(vertices[0])
                vertices = np.array(vertices)
                # Compute the area with the Shoelace formula. TODO : sort the vertices or find a better criterion
                area = 0.5 * np.abs(np.dot(vertices[:-1, 0], np.roll(vertices[:-1, 1], 1)) -
                                    np.dot(vertices[:-1, 1], np.roll(vertices[:-1, 0], 1)))
                print("area", area)
                if area > 500000:
                    self.confidence = PHENOMENON_ENCLOSED_CONFIDENCE
                    self.interpolate()
                    # Place the origin of the terrain at the center
                    self.shift(self.shape.mean(axis=0).astype(int))

    def recognize(self, category):
        """Set the terrain's category, shape, path, confidence. Adjust its position to the latest affordance"""
        super().recognize(category)

        # TODO Manage the delete absolute affordance
        if self.absolute_affordance() is None:
            return

        # TODO The phenomenon position is different if the phenomenon is recognized from a black line
        # The TERRAIN direction depends on the orientation of the absolute affordance
        if np.dot(self.absolute_affordance().polar_sensor_point, category.quaternion * Vector3([1., 0., 0.])) < 0:
            # Origin is North-East
            self.origin_direction_quaternion = category.quaternion.copy()
        else:
            # Origin is South-West
            self.origin_direction_quaternion = category.quaternion * Quaternion.from_z_rotation(math.pi)

        # The new relative origin is the position of green patch from the phenomenon center
        y = (MIDDLE_COLOR_INDEX - self.absolute_affordance().color_index) * COLOR_DISTANCE
        new_origin = np.array(self.origin_direction_quaternion * Vector3([category.long_radius, y, 0]), dtype=int)

        # The position of the phenomenon is adjusted by the difference in relative origin
        terrain_offset = new_origin - self.relative_origin_point
        # print("Terrain offset", terrain_offset)
        self.point -= terrain_offset
        for a in self.affordances.values():
            a.point += terrain_offset
        self.relative_origin_point = new_origin

    def confirmation_prompt(self):
        """Return the point in polar egocentric coordinates to aim for confirmation of this phenomenon"""
        # Aim parallel to the origin direction from the relative origin point
        return self.relative_origin_point + self.origin_direction_quaternion * Vector3([500, 0, 0])

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin: " + str(self.point[0]) + "," + str(self.point[1])
        return label

    def vector_toward_origin(self, affordance):
        """Return the distance between the affordance's green point and the origin point"""
        # Positive prediction error means reducing the position computed through path integration
        # The prediction error must be subtracted from the computed position

        # The color point along the y axis: red positive, purple negative.
        color_y = Vector3([0, (MIDDLE_COLOR_INDEX - affordance.color_index) * COLOR_DISTANCE, 0])

        if abs(short_angle(affordance.quaternion, self.origin_direction_quaternion)) < math.pi / 2:
            # Vector to origin
            # Trust the terrain direction
            # v = affordance.point + affordance.polar_sensor_point - self.origin_direction_quaternion * color_y - self.relative_origin_point
            v = affordance.point - self.origin_direction_quaternion * color_y - self.relative_origin_point
            # Trust the affordance direction
            # v = affordance.point + affordance.polar_green_point() - self.relative_origin_point
        else:
            # Vector to opposite of the origin
            # Trust the terrain direction
            # v = affordance.point + affordance.polar_sensor_point + self.origin_direction_quaternion * color_y + self.relative_origin_point
            v = affordance.point + self.origin_direction_quaternion * color_y + self.relative_origin_point
            # Trust the affordance direction
            # v = affordance.point + affordance.polar_green_point() + self.relative_origin_point
        # print("Place prediction error", v)
        return np.array(v, dtype=int)

    def prune(self, affordance):
        """Remove previous affordances that has the closest angle"""
        q_affordance = Quaternion.from_z_rotation(math.atan2(affordance.point[1], affordance.point[0]))
        similar_affordances = []
        for k, a in self.affordances.items():
            q_from_center = Quaternion.from_z_rotation(math.atan2(a.point[1], a.point[0]))
            # TODO check that it's ok to remove affordance 0
            if abs(short_angle(q_from_center, q_affordance)) < math.pi / 8 and k < self.affordance_id - 2:
                similar_affordances.append(k)

        for k in similar_affordances:
            print("Prune affordance", k)
            self.affordances.pop(k)

    # def prune(self, theta_rad):
    #     """Keep only affordances whose directions are spread from the last by more than theta_rad"""
    #     last_q = Quaternion.from_z_rotation(math.atan2(self.affordances[self.affordance_id].point[1],
    #                                                    self.affordances[self.affordance_id].point[0]))
    #     self.affordances = {k: a for k, a in self.affordances if
    #                         abs(short_angle(Quaternion.from_z_rotation(math.atan2(a.point[1], a.point[0])), last_q)) <
    #                         theta_rad and k < self.affordance_id}

    def save(self, saved_phenomenon=None):
        """Return a clone of the phenomenon for memory snapshot"""
        # Instantiate the clone using the first affordance of the phenomenon
        saved_phenomenon = PhenomenonTerrain(self.affordances[min(self.affordances)].save())
        super().save(saved_phenomenon)
        return saved_phenomenon
