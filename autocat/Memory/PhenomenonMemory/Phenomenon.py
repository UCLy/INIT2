import math
import numpy as np
from scipy.spatial import ConvexHull, QhullError, Delaunay

PHENOMENON_DELTA = 300  # (mm) Distance between affordances to be considered the same phenomenon
PHENOMENON_INITIAL_CONFIDENCE = 0.0  # 0.2 Initial confidence in the phenomenon
PHENOMENON_CONFIDENCE_PRUNE = 0.3  # Confidence threshold above which prune


class Phenomenon:
    """The parent class of all phenomena types"""
    def __init__(self, affordance):
        """Constructor
        Parameters:
            affordance: the first affordance that serves as the origin of the phenomenon
            """
        self.confidence = PHENOMENON_INITIAL_CONFIDENCE

        # Record the first affordance of the phenomenon
        self.point = affordance.point.copy().astype(int)  # The position of the phenomenon = position of the first affordance
        affordance.point = np.array([0, 0, 0], dtype=int)  # Position of the first affordance is reset
        self.affordances = {0: affordance}
        self.affordance_id = 0
        self.absolute_affordance_key = None

        self.nb_tour = 0
        self.tour_started = False
        # The hull is used to display the phenomenon's contour
        self.hull_array = None
        # Last time the origin affordance was enacted. Used to compute the return to origin.
        self.last_origin_clock = affordance.experience.clock

    def absolute_affordance(self):
        """Return a reference to the absolute origin affordance or None"""
        if self.absolute_affordance_key is None:
            return None
        return self.affordances[self.absolute_affordance_key]

    def compute_center(self):
        """Recompute the center of the phenomenon as the mean of the affordance position"""
        # https://stackoverflow.com/questions/4355894/how-to-get-center-of-set-of-points-using-python
        points = np.array([a.point for a in self.affordances.values()])
        centroid = points.mean(axis=0)
        return centroid

    def convex_hull(self):
        """Return the points of the convex hull containing the phenomenon as a flat list"""
        hull_points = None
        # ConvexHull triggers errors if points are aligned
        try:
            points = np.array([a.point[0:2] for a in self.affordances.values()])
            hull = ConvexHull(points)
            self.hull_array = np.array([points[vertex] for vertex in hull.vertices])
            hull_points = self.hull_array.flatten().astype("int").tolist()
        except QhullError:
            print("Error computing the convex hull: probably not enough points.")
        except IndexError as e:
            print("Error computing the convex hull: probably not enough points.", e)
        return hull_points

    def is_inside(self, p):
        """True if p is inside the convex hull"""
        # https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl
        is_inside = False
        try:
            # Must reduce to 2 dimensions otherwise the point is not found inside
            d = Delaunay(self.hull_array)  # The hull array is computed at the end of the previous cycle
            is_inside = (d.find_simplex(p[0:2]) >= 0)
        except IndexError as e:
            print("Error computing the Delaunay: ", e)
        return is_inside

    def phenomenon_label(self):
        """Return the text to display in phenomenon view"""
        label = "Origin direction: " + \
            str(round(math.degrees(self.affordances[0].experience.absolute_direction_rad))) + \
            "°. Nb tours:" + str(self.nb_tour)
        return label

    def save(self, saved_phenomenon, experiences):
        """Return a clone of the phenomenon for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon.point = self.point.copy()
        saved_phenomenon.confidence = self.confidence
        saved_phenomenon.nb_tour = self.nb_tour
        saved_phenomenon.tour_started = self.tour_started
        saved_phenomenon.affordances = {key: a.save(experiences) for key, a in self.affordances.items()}
        saved_phenomenon.affordance_id = self.affordance_id
        saved_phenomenon.absolute_affordance_key = self.absolute_affordance_key
        saved_phenomenon.last_origin_clock = self.last_origin_clock
        return