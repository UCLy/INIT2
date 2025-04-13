import math
import numpy as np
from .InteractiveWindow import InteractiveWindow
from pyglet.window import key
from ..Memory.PlaceMemory.PlaceGeometry import compare_all_place_cells
from ..Enaction import KEY_ENGAGEMENT_ROBOT, KEY_CONTROL_DECIDER, KEY_ENGAGEMENT_IMAGINARY
from ..Proposer.Action import create_actions, ACTION_FORWARD, ACTIONS, ACTION_TURN, ACTION_BACKWARD
from ..Enaction.CompositeEnaction import CompositeEnaction
from ..Proposer.Interaction import OUTCOME_PROMPT, create_interactions
from ..SoundPlayer import SoundPlayer, SOUND_CLEAR
from ..Robot.Enaction import Enaction
from ..Robot.Command import DIRECTION_BACK
from ..Enaction import ENACTION_STEP_RENDERING


KEY_CONTROL_USER = "M"  # Manual mode : controlled by the user
KEY_CLEAR = "C"  # Clear the stack of interactions to enact next
KEY_PREDICTION_ERROR = "E"  # Compute the prediction errors
KEY_ENCLOSE = "N"
KEY_POSITION = "P"
KEY_COMPARE = ""
KEY_SAVE = "S"


class CtrlWindow:
    """The parent class of the controller of all the pyglet windows"""

    def __init__(self, workspace):
        self.view = InteractiveWindow()
        self.workspace = workspace

        def on_text(text):
            """Handle user keypress"""
            # self.workspace.process_user_key(text)
            self.process_user_key(text)

        self.view.on_text = on_text

        def on_mouse_motion(x, y, dx, dy):
            """Display the position in allocentric memory and the cell in the grid"""
            ego_point = self.view.window_to_ego_centric(x, y)
            self.display_mouse(ego_point)

        def on_key_press(symbol, modifiers):
            """handle single key press"""
            # F1: save the comparison of the current place cells with all others
            if symbol == key.F1:
                cell_id = self.workspace.memory.place_memory.current_cell_id
                print(f"Comparing cell {cell_id} to other fully observed cells")
                if cell_id > 0:
                    compare_all_place_cells(cell_id, self.workspace.memory.place_memory.place_cells)
            # F2: start a new subgraph
            if symbol == key.F2:
                self.workspace.memory.place_memory.graph_start_id = self.workspace.memory.place_memory.place_cell_id + 1
            # F3:

        # Add the event functions to the window
        # self.view.push_handlers(on_text, on_mouse_motion, on_key_press)
        self.view.push_handlers(on_mouse_motion, on_key_press)

    def display_mouse(self, ego_point):
        """Display the mouse information"""
        ego_angle = math.degrees(math.atan2(ego_point[1], ego_point[0]))
        self.view.label3.text = f"Ego: {tuple(ego_point[:2])}, {ego_angle:.0f}°"

    def process_user_key(self, user_key):
        """Process the keypress on the view windows (called by the views)"""
        if user_key.upper() in [KEY_CONTROL_DECIDER, KEY_CONTROL_USER]:
            self.workspace.control_mode = user_key.upper()
        elif user_key.upper() in [KEY_ENGAGEMENT_ROBOT, KEY_ENGAGEMENT_IMAGINARY]:
            self.workspace.engagement_mode = user_key.upper()
        elif user_key.upper() in ACTIONS:
            i0 = self.workspace.primitive_interactions[(user_key.upper(), OUTCOME_PROMPT)]
            self.workspace.manual_composite_interaction = CompositeEnaction(
                None, 'Manual', np.array([1, 1, 1]), [i0], self.workspace.memory.save())
            # if the stack is empty then add this interaction to the stack
            if self.workspace.composite_enaction is None:
                self.workspace.composite_enaction = self.workspace.manual_composite_interaction
                self.workspace.manual_composite_interaction = None
                # i0 = self.workspace.primitive_interactions[(user_key.upper(), OUTCOME_PROMPT)]
                # self.workspace.composite_enaction = CompositeEnaction(None, 'Manual', np.array([1, 1, 1]), [i0], self.workspace.memory.save())

        elif user_key.upper() == "/":
            # If key ALIGN then turn and move forward to the prompt
            self.workspace.manual_composite_interaction = CompositeEnaction(
                None, 'Manual', np.array([1, 1, 1]), self.workspace.sequence_interactions["TF-P"],
                self.workspace.memory.save())
            if self.workspace.composite_enaction is None:
                self.workspace.composite_enaction = self.workspace.manual_composite_interaction
                self.workspace.manual_composite_interaction = None
        elif user_key.upper() == ":" and self.workspace.memory.egocentric_memory.focus_point is not None:
            # If key ALIGN BACK then turn back and move backward to the prompt
            if self.workspace.composite_enaction is None:
            # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
                # The first enaction: turn the back to the prompt
                i0 = self.workspace.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
                e0 = Enaction(i0, self.workspace.memory.save(), direction=DIRECTION_BACK)
                # Second enaction: move forward to the prompt
                i1 = self.workspace.primitive_interactions[(ACTION_BACKWARD, OUTCOME_PROMPT)]
                e1 = Enaction(i1, e0.predicted_memory.save())
                self.composite_enaction = CompositeEnaction([e0, e1], 'Manual', np.array([1, 1, 1]))
        # elif user_key.upper() == "P" and self.memory.egocentric_memory.focus_point is not None:
        #     # If key PUSH and has focus then create the push sequence
        #     if self.composite_enaction is None:
        #     # if self.enacter.interaction_step == ENACTION_STEP_IDLE:
        #         # First enaction: turn to the prompt
        #         i0 = self.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
        #         e0 = Enaction(i0, self.memory.save())
        #         # Second enaction: move forward to the prompt
        #         i1 = self.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
        #         e1 = Enaction(i1, e0.predicted_memory.save())
        #         # Third enaction: turn to the prompt which is copied from the focus because it may be cleared
        #         i2 = self.primitive_interactions[(ACTION_TURN, OUTCOME_PROMPT)]
        #         e2_memory = e1.predicted_memory.save()
        #         e2_memory.egocentric_memory.prompt_point = e1.predicted_memory.egocentric_memory.focus_point.copy()
        #         e2 = Enaction(i2, e2_memory)
        #         # Fourth enaction: move forward to the new prompt
        #         i3 = self.primitive_interactions[(ACTION_FORWARD, OUTCOME_PROMPT)]
        #         e3 = Enaction(i3, e2.predicted_memory.save())
        #         self.composite_enaction = CompositeEnaction([e0, e1, e2, e3], 'Manual', np.array([1, 1, 1]))
        elif user_key.upper() == KEY_CLEAR:
            # Clear the current composite enaction and reset the enaction cycle
            SoundPlayer.play(SOUND_CLEAR)
            self.workspace.composite_enaction = None
            # Restore memory
            neurotransmitter_point = self.workspace.memory.body_memory.neurotransmitters.copy()
            confidence = self.workspace.memory.phenomenon_memory.terrain_confidence()
            self.workspace.memory = self.workspace.enacter.memory_snapshot
            self.workspace.memory.body_memory.neurotransmitters[:] = neurotransmitter_point
            if self.workspace.memory.phenomenon_memory.terrain() is not None:
                self.workspace.memory.phenomenon_memory.terrain().confidence = confidence
            self.workspace.enacter.interaction_step = ENACTION_STEP_RENDERING
            # TODO: prevent a crash when the enaction has been cleared and then an outcome is received after
        elif user_key.upper() == KEY_PREDICTION_ERROR:
            self.workspace.prediction_error.plot()
        elif user_key.upper() == KEY_POSITION:
            # Move the robot by the position correction from place cell memory
            self.workspace.memory.adjust_robot_position()
            self.workspace.show_place_cell(self.workspace.memory.place_memory.current_cell_id)
            self.workspace.enacter.interaction_step = ENACTION_STEP_RENDERING
        elif user_key.upper() == KEY_SAVE:
            self.view.save()
