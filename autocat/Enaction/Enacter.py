import numpy as np
from ..Robot.CtrlRobot import ENACTION_STEP_IDLE, ENACTION_STEP_COMMANDING, ENACTION_STEP_ENACTING, \
    ENACTION_STEP_INTEGRATING, ENACTION_STEP_RENDERING
from ..Memory.PhenomenonMemory import TERRAIN_ORIGIN_CONFIDENCE
from ..Integrator.OutcomeCode import outcome_code, outcome_code_focus
from . import KEY_ENGAGEMENT_ROBOT, KEY_CONTROL_DECIDER, KEY_ENGAGEMENT_IMAGINARY
from ..Robot.RobotDefine import ROBOT_FLOOR_SENSOR_X
from ..Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR
from ..Proposer.Interaction import OUTCOME_LOST_FOCUS, OUTCOME_NO_FOCUS
from ..Proposer.Proposer import Proposer
from ..Proposer.ProposerFocusPhenomenon import ProposerFocusPhenomenon
from ..Proposer.ProposerExplore import ProposerExplore
from ..Proposer.ProposerWatch import ProposerWatch
from ..Proposer.ProposerPush import ProposerPush
from ..Proposer.ProposerWatchCenter import ProposerWatchCenter
from ..Proposer.ProposerArrange import ProposerArrange
from ..Proposer.ProposerPlayForward import ProposerPlayForward
from ..Proposer.ProposerPlayTurn import ProposerPlayTurn
from ..Proposer.ProposerPlaySwipe import ProposerPlaySwipe
from ..Proposer.ProposerPlayTerrain import ProposerPlayTerrain
from ..SoundPlayer import SoundPlayer, SOUND_SURPRISE
from ..Proposer.AttentionMechanism import AttentionMechanism


class Enacter:
    def __init__(self, workspace):
        self.workspace = workspace
        self.attention_mechanism = AttentionMechanism(workspace)
        self.interaction_step = ENACTION_STEP_IDLE
        self.memory_snapshot = None
        self.is_imagining = False
        self.memory_before_imaginary = None
        self.proposers = {'Default': Proposer(self.workspace)
                          # , 'Play Turn': ProposerPlayTurn(self)
                          # , 'Explore': ProposerExplore(self)
                          # , 'Watch': ProposerWatch(self.workspace)
                          # , 'Watch C': ProposerWatchCenter(self),  'Arrange': ProposerArrange(self)
                          # , 'Push': ProposerPush(self.workspace)
                          # , 'Play': ProposerPlayForward(self)
                          # , "Play terrain": ProposerPlayTerrain(self)
                          , "Point": ProposerFocusPhenomenon(self.workspace)
                          }

    def main(self, dt):
        """Controls the enaction."""
        # RENDERING: last only one cycle
        if self.interaction_step == ENACTION_STEP_RENDERING:
            self.interaction_step = ENACTION_STEP_IDLE

        # IDLE: Ready to choose the next intended interaction
        if self.interaction_step == ENACTION_STEP_IDLE:
            # Manage the memory snapshot
            if self.is_imagining:
                # If stop imagining then restore memory from the snapshot
                if self.workspace.engagement_mode == KEY_ENGAGEMENT_ROBOT:
                    self.workspace.memory = self.memory_before_imaginary
                    self.is_imagining = False
                    self.interaction_step = ENACTION_STEP_RENDERING
            else:
                # If start imagining then take a new memory snapshot
                if self.workspace.engagement_mode == KEY_ENGAGEMENT_IMAGINARY:
                    self.memory_before_imaginary = self.workspace.memory.save()
                    self.is_imagining = True
            # Next automatic decision
            if self.workspace.composite_enaction is None:
                if self.workspace.control_mode == KEY_CONTROL_DECIDER:
                    # All deciders propose an enaction with an activation value
                    self.workspace.composite_enaction = self.decide()
                else:
                    self.workspace.decider_id = "Manual"
                # Case DECIDER_KEY_USER is handled by self.process_user_key()

            # When the next enaction is in the stack, prepare the enaction
            if self.workspace.composite_enaction is not None:
                # Take the current enaction from the composite interaction
                self.workspace.enaction = self.workspace.composite_enaction.current_enaction()
                # Take a memory snapshot to restore at the end of the enaction
                # self.workspace.memory.emotion_code = self.workspace.enaction.predicted_memory.emotion_code
                self.memory_snapshot = self.workspace.memory.save()
                # Show the prompt in memory
                if self.workspace.enaction.trajectory.prompt_point is not None:
                    self.workspace.memory.egocentric_memory.prompt_point = self.workspace.enaction.trajectory.prompt_point.copy()
                    self.workspace.memory.allocentric_memory.update_prompt(self.workspace.memory.egocentric_to_allocentric(self.workspace.memory.egocentric_memory.prompt_point), self.workspace.memory.clock)
                # Begin the enaction
                self.workspace.enaction.begin(self.workspace.memory.body_memory.body_quaternion)
                # Begin the simulation
                self.workspace.simulator.begin()
                if self.is_imagining:
                    # If imagining then proceed to simulating the enaction
                    self.interaction_step = ENACTION_STEP_ENACTING
                else:
                    # If not imagining then proceed to COMMANDING to send the command to the robot
                    self.interaction_step = ENACTION_STEP_COMMANDING

        # COMMANDING: CtrlRobot sends the command to the robot and moves on to ENACTING

        # ENACTING: Simulate the enaction in memory
        if self.interaction_step == ENACTION_STEP_ENACTING:
            self.workspace.simulator.simulate(dt)
            # If imagining then check for the end of the simulation
            if self.is_imagining and not self.workspace.simulator.is_simulating:
                # simulated_outcome = self.workspace.simulator.end()
                # self.workspace.enaction.terminate(simulated_outcome)
                self.interaction_step = ENACTION_STEP_INTEGRATING
            # If not imagining then CtrlRobot will terminate the enaction and proceed to INTEGRATING

        # INTEGRATING: the new enacted interaction
        if self.interaction_step == ENACTION_STEP_INTEGRATING:
            # Terminate the simulation
            simulated_outcome = self.workspace.simulator.end()
            print("Simulated outcome", simulated_outcome)
            if self.is_imagining:
                self.workspace.enaction.outcome = simulated_outcome

            # Terminate the enaction using the outcome that come from the robot or from the simulation
            self.workspace.enaction.terminate()

            # Restore the memory from the snapshot
            neurotransmitters = self.workspace.memory.body_memory.neurotransmitters.copy()
            confidence = self.workspace.memory.phenomenon_memory.terrain_confidence()
            self.workspace.memory = self.memory_snapshot
            self.workspace.memory.body_memory.neurotransmitters[:] = neurotransmitters
            if self.workspace.memory.phenomenon_memory.terrain() is not None:
                self.workspace.memory.phenomenon_memory.terrain().confidence = confidence

            # Retrieve possible message from other robot
            if self.workspace.memory.phenomenon_memory.terrain_confidence() >= TERRAIN_ORIGIN_CONFIDENCE and \
                    self.workspace.message is not None:
                self.workspace.enaction.message = self.workspace.message
                print("Message", self.workspace.message.message_string)

            # Update memory, possibly create new place cell and phenomena
            self.workspace.memory.update(self.workspace.enaction)
            # Show the current place cell in PlaceCellView
            self.workspace.show_place_cell(self.workspace.memory.place_memory.current_robot_cell_id)

            # Select the focus - May be included in the attention mechanism
            # self.select_focus(self.workspace.memory)

            # Compute the outcome code which depends on the updated memory
            self.workspace.enaction.outcome_code = outcome_code(self.workspace.memory,
                                                   self.workspace.enaction.trajectory, self.workspace.enaction.outcome)

            # Express surprise if the enaction failed
            if not self.workspace.enaction.succeed():
                SoundPlayer.play(SOUND_SURPRISE)
                # if failed due to no floor and no impact
                if self.workspace.enaction.outcome.floor == 0 and \
                        self.workspace.memory.phenomenon_memory.focus_phenomenon_id is not None \
                        and self.workspace.enaction.outcome.impact == 0:
                    # Lost focus to DOT phenomenon  TODO improve
                    self.workspace.enaction.outcome_code = OUTCOME_LOST_FOCUS

            # Manage attention
            # Focus at the nearest phenomenon, or near the dot phenomenon it if it was lost
            self.attention_mechanism.update_focus()
            if self.workspace.memory.egocentric_memory.focus_point is not None and self.workspace.enaction.outcome_code == OUTCOME_NO_FOCUS:
                self.workspace.enaction.outcome_code = outcome_code_focus(self.workspace.memory.egocentric_memory.focus_point, self.workspace.memory)

            # Track the prediction errors
            self.workspace.prediction_error.log(self.workspace.enaction)
            # Calibrate
            self.workspace.calibrator.calibrate()

            # Increment the clock
            if self.workspace.enaction.clock >= self.workspace.memory.clock:  # don't increment if the robot is behind
                self.workspace.memory.clock += 1
            else:
                print("Clock not incremented")  # TODO If never happens then remove the test

            # If the composite enaction is over or aborted due to floor or impact
            if not self.workspace.composite_enaction.increment():
                self.workspace.composite_enaction = None

            self.interaction_step = ENACTION_STEP_RENDERING

        # RENDERING: Will be reset to IDLE in the next cycle
        # if self.interaction_step == ENACTION_STEP_RENDERING:
        #     print("Render the views")

    def decide(self):
        """Return the selected composite enaction"""
        # Update the focus is the dot was lost
        # self.attention_mechanism.update_focus()

        # Each proposer adds a proposition to the list
        propositions = []
        for proposer in self.proposers.values():
            # activation = proposer.activation_level()  # Must compute before proposing
            enaction = proposer.propose_enaction()
            if enaction is not None:
                print("Proposition", enaction, "with focus", self.workspace.memory.egocentric_memory.focus_point)
                activation = enaction.emotion_mask * self.workspace.memory.body_memory.neurotransmitters
                propositions.append([enaction, activation.sum()])
        print("Proposed enactions:")
        for p in propositions:
            print(" ", p[0].decider_id, ":", p[0], p[1])
            # print(" ", p[0], ":", p[1], p[2])

        # Select the enaction that has the highest activation value
        most_activated_index = propositions.index(max(propositions, key=lambda p: p[1]))
        self.workspace.decider_id = propositions[most_activated_index][0].decider_id
        print("Decider:", self.workspace.decider_id)
        return propositions[most_activated_index][0]

    def select_focus(self, memory):
        """Select a focus based on the phenomena in memory"""

        # Look for DOT phenomena
        k_d = {k: memory.allocentric_to_egocentric(p.point)[0] for k, p in memory.phenomenon_memory.phenomena.items()
               if p.phenomenon_type == EXPERIENCE_FLOOR and memory.allocentric_to_egocentric(p.point)[0] >
               ROBOT_FLOOR_SENSOR_X}
        if len(k_d) > 0:
            # Focus at the closest DOT phenomenon
            closest_key = min(k_d, key=k_d.get)
            memory.phenomenon_memory.focus_phenomenon_id = closest_key
            closest_dot_phenomenon = memory.phenomenon_memory.phenomena[closest_key]
            memory.allocentric_memory.update_focus(closest_dot_phenomenon.point, memory.clock)
            memory.egocentric_memory.focus_point = memory.allocentric_to_egocentric(closest_dot_phenomenon.point)

        # # If no focus then look for phenomena that could attract focus
        # if memory.egocentric_memory.focus_point is None:
        #     # The dict of distances of the dot phenomena beyond the floor sensor
        #     k_d = {k: memory.allocentric_to_egocentric(p.point)[0] for k, p in memory.phenomenon_memory.phenomena.items()
        #            if p.phenomenon_type == EXPERIENCE_FLOOR and memory.allocentric_to_egocentric(p.point)[0] > ROBOT_FLOOR_SENSOR_X}
        #     if len(k_d) > 0:
        #         # Focus at the closest phenomenon
        #         closest_key = min(k_d, key=k_d.get)
        #         memory.phenomenon_memory.focus_phenomenon_id = closest_key
        #         closest_dot_phenomenon = memory.phenomenon_memory.phenomena[closest_key]
        #         memory.allocentric_memory.update_focus(closest_dot_phenomenon.point, memory.clock)
        #         memory.egocentric_memory.focus_point = memory.allocentric_to_egocentric(closest_dot_phenomenon.point)
