import numpy as np
from .PhenomenonObject import PhenomenonObject, OBJECT_EXPERIENCE_TYPES
from .PhenomenonTerrain import PhenomenonTerrain, TERRAIN_EXPERIENCE_TYPES

TER = 0


class PhenomenonMemory:
    def __init__(self):
        self.phenomena = {}  # Phenomenon 0 is the terrain
        self.phenomenon_id = 0  # Used for object phenomena

    def create_phenomenon(self, affordance):
        """Create a new phenomenon depending of the type of the affordance"""
        # Must always create a phenomenon
        if affordance.experience.type in TERRAIN_EXPERIENCE_TYPES:
            self.phenomena[TER] = PhenomenonTerrain(affordance)
            return 0
        else:
            self.phenomenon_id += 1
            self.phenomena[self.phenomenon_id] = PhenomenonObject(affordance)
            return self.phenomenon_id

    def create_phenomena(self, affordances):
        """Create new phenomena from the list of affordances"""
        new_phenomena_id = []
        for affordance in affordances:
            if len(new_phenomena_id) == 0:
                new_phenomena_id.append(self.create_phenomenon(affordance))
            else:
                clustered = False
                # Look if the new affordance can be attached to an existing new phenomenon
                for new_phenomenon_id in new_phenomena_id:
                    print("Update new phenomenon")
                    if self.phenomena[new_phenomenon_id].update(affordance) is not None:
                        clustered = True
                        break
                if not clustered:
                    new_phenomena_id.append(self.create_phenomenon(affordance))
        # self.object_phenomena.extend(new_phenomena_id)

    def update_phenomena(self, affordances):
        """Try to attach a list of affordances to phenomena in the list.
        Returns the affordances that have not been attached, and the average translation"""
        position_correction = np.array([0, 0, 0], dtype=int)
        sum_translation = np.array([0, 0, 0], dtype=int)
        number_of_add = 0
        remaining_affordances = affordances.copy()

        for affordance in affordances:
            for phenomenon in self.phenomena.values():
                delta = phenomenon.update(affordance)
                if delta is not None:
                    remaining_affordances.remove(affordance)
                    # Null correction do not count (to be improved)
                    if round(np.linalg.norm(delta)) > 0:
                        sum_translation += delta.astype(int)
                        number_of_add += 1
                    # Don't look the other phenomena
                    break
        if number_of_add > 0:
            position_correction = np.divide(sum_translation, number_of_add)

        return remaining_affordances, position_correction

    def save(self, experiences):
        """Return a clone of phenomenon memory for memory snapshot"""
        # Use the experiences cloned when saving egocentric memory
        saved_phenomenon_memory = PhenomenonMemory()
        saved_phenomenon_memory.phenomena = {key: p.save(experiences) for key, p in self.phenomena.items()}
        saved_phenomenon_memory.phenomenon_id = self.phenomenon_id
        return saved_phenomenon_memory