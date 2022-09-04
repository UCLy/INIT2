from autocat.Memory.EgocentricMemory.Experience import Experience
from autocat.Memory.EgocentricMemory.Experience import EXPERIENCE_LOCAL_ECHO
import math
from pyrr import matrix44

INTERACTION_PERSISTENCE = 5


class EgocentricMemory:
    """This class play the role of a memory manager : it stocks Interaction objects,
    apply transformations to them (such as decay)
    and also as the responsibility to translate them to concrete shapes on the GUI.
    
    This aims to make both Interaction and the view modulable.

    Author: TKnockaert
    """

    def __init__(self):
        self.experiences = []
        self.current_id = 0

    def reset(self):
        self.experiences = []
        self.current_id = 0

    def assimilate(self, enacted_interaction):
        """ Process the enacted interaction to update the egocentric memory
        - Move the previous interactions
        - Add new interactions
        """

        # Move the existing interactions
        for interaction in self.experiences:
            interaction.displace(enacted_interaction['displacement_matrix'])

        # self.last_enacted_interaction = enacted_interaction
        # Create experiences from points in the enacted_interaction
        for p in enacted_interaction['points']:
            interaction = Experience(p[1], p[2], 10, 10, experience_type=p[0], experience_id=self.current_id,
                                     durability=INTERACTION_PERSISTENCE)
            self.experiences.append(interaction)
            self.current_id += 1

    # def add_echo_array(self, echo_array):
        if 'echo_array' in enacted_interaction:
            echo_array = enacted_interaction['echo_array']
            for _, echo in enumerate(echo_array):
                x = echo[0]
                #print("add_echo_array, x :",x)
                y = echo[1]
                local_echo_interaction = Experience(x, y, width=15, experience_type=EXPERIENCE_LOCAL_ECHO,
                                                    durability=INTERACTION_PERSISTENCE, decay_intensity=1,
                                                    experience_id=self.current_id)
                self.experiences.append(local_echo_interaction)
                self.current_id += 1

    def tick(self):
        for p in self.experiences:
            p.tick()
        # Remove the interactions when they are too old
        to_remove = []
        for i in self.experiences:
            if i.actual_durability <= 0:
                to_remove.append(i)
        self.experiences = [x for x in self.experiences if x not in to_remove]

    def empty(self):
        self.experiences.clear()

    # def move(self, rotation, translation):
    #     """ Compute the displacement matrix and apply it to the interactions """
    #     translation_matrix = matrix44.create_from_translation([-translation[0], -translation[1], 0])
    #     rotation_matrix = matrix44.create_from_z_rotation(math.radians(rotation))
    #     displacement_matrix = matrix44.multiply(rotation_matrix, translation_matrix)
    #     # Translate and rotate all the interactions
    #     for interaction in self.interactions:
    #         interaction.displace(displacement_matrix)

    def last_action(self):
        return self.actions[-1] if len(self.actions) > 0 else None

