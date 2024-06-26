from ..Robot.Enaction import Enaction
from ..Proposer.Action import ACTION_SCAN
from ..Proposer.Interaction import OUTCOME_FLOOR, OUTCOME_FOCUS_FRONT


class CompositeEnaction:
    """A composite enaction is a series of primitive interactions"""
    def __init__(self, enactions, decider_id, emotion_mask, interactions=None, memory=None):
        self.enactions = enactions
        self.index = 0
        self.decider_id = decider_id
        self.emotion_mask = emotion_mask

        # Construct the list of enactions from the list of interactions if any
        if interactions is not None:
            self.enactions = []
            # e_memory = memory
            for interaction in interactions:
                if decider_id == 'Manual' and interaction.action.action_code == ACTION_SCAN:
                    span = 10
                else:
                    span = 40
                # Modify the prompt depending on the intended outcome
                if interaction.outcome == OUTCOME_FLOOR:
                    memory.egocentric_memory.prompt_point = None
                elif interaction.outcome == OUTCOME_FOCUS_FRONT:
                    if memory.egocentric_memory.focus_point is not None:
                        memory.egocentric_memory.prompt_point = memory.egocentric_memory.focus_point.copy()
                    else:
                        memory.egocentric_memory.prompt_point = None

                e = Enaction(interaction, memory, span=span)
                memory = e.predicted_memory.save()
                self.enactions.append(e)

        self.key = tuple([e.key for e in self.enactions])

    def __hash__(self):
        """The hash is the action code """
        """Return the hash computed from the __key"""
        return hash(self.key)

    def __eq__(self, other):
        """Composite enactions are equal if they have the same keys"""
        if isinstance(other, CompositeEnaction):
            return self.key == other.key
        # TODO implement comparison with primitive enactions
        return NotImplemented

    def __str__(self):
        """Return a representation of the key tuple"""
        return self.key.__str__()

    def current_enaction(self):
        """Return the enaction at the current index"""
        assert self.index < len(self.enactions)
        return self.enactions[self.index]

    def increment(self):
        """Move on to the next interaction or return False if end"""
        # If the primitive enaction failed then abort
        if not self.enactions[self.index].succeed():
            return False
        self.index += 1
        # If no more enactions then return False
        if self.index >= len(self.enactions):
            return False
        return True
