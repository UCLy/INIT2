import time
import numpy as np
from pyglet.window import key, mouse
from .AllocentricView import AllocentricView
from ...Memory.AllocentricMemory.Geometry import point_to_cell
# from ...Robot.CtrlRobot import ENACTION_STEP_RENDERING, ENACTION_STEP_ENACTING
from ...Enaction import ENACTION_STEP_RENDERING, ENACTION_STEP_ENACTING
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_FLOOR, EXPERIENCE_ALIGNED_ECHO
from ...Memory.AllocentricMemory.AllocentricMemory import CELL_UNKNOWN
from ...Memory.AllocentricMemory import STATUS_FLOOR, STATUS_2, STATUS_ECHO, STATUS_3, STATUS_4, COLOR_INDEX, CLOCK_FOCUS, \
    CLOCK_PLACE, PHENOMENON_ID, PLACE_CELL_ID, CLOCK_UPDATED, CLOCK_PROMPT
from ...Memory import PLACE_GRID_DURABILITY
from ..CtrlWindow import KEY_SAVE


class CtrlAllocentricView:
    def __init__(self, workspace):
        """Control the allocentric view"""
        self.workspace = workspace
        self.view = AllocentricView()
        self.view.set_caption("Allocentric " + workspace.robot_id)
        self.next_time_refresh = 0

        # Handlers of event functions that need access to workspace
        def on_text(text):
            """Send user keypress to the workspace to handle"""
            if text.upper() == KEY_SAVE:
                print("saving allocentric")
                self.view.save()
            else:
                self.workspace.process_user_key(text)

        self.view.on_text = on_text

        def on_mouse_press(x, y, button, modifiers):
            """Display the label of this cell"""
            click_point = self.view.mouse_coordinates_to_point(x, y)
            cell_x, cell_y = point_to_cell(click_point)
            selected_cell = self.workspace.memory.allocentric_memory.grid[cell_x][cell_y]

            # Change cell status
            if button == mouse.RIGHT:
                # SHIFT clear the cell and the prompts
                if modifiers & key.MOD_SHIFT:
                    self.delete_prompt()
                    # Clear the FLOOR status
                    self.workspace.memory.allocentric_memory.clear_cell(cell_x, cell_y, self.workspace.memory.clock)
                    if (cell_x, cell_y) in self.workspace.memory.allocentric_memory.user_cells:
                        self.workspace.memory.allocentric_memory.user_cells.remove((cell_x, cell_y))
                # CTRL ALT: toggle COLOR FLOOR
                elif modifiers & key.MOD_CTRL and modifiers & key.MOD_ALT:
                    if selected_cell[STATUS_FLOOR] == EXPERIENCE_FLOOR and selected_cell[COLOR_INDEX] > 0:
                        selected_cell[STATUS_FLOOR] = CELL_UNKNOWN
                        selected_cell[COLOR_INDEX] = 0
                        #cell.color_index = 0
                        if (cell_x, cell_y) in self.workspace.memory.allocentric_memory.user_cells:
                            self.workspace.memory.allocentric_memory.user_cells.remove((cell_x, cell_y))
                    else:
                        # Mark a green FLOOR cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_FLOOR,
                                                                                      self.workspace.memory.clock, 4)
                        self.workspace.memory.allocentric_memory.user_cells.append((cell_x, cell_y))
                # CTRL: Toggle FLOOR
                elif modifiers & key.MOD_CTRL:
                    if selected_cell[STATUS_FLOOR] == EXPERIENCE_FLOOR and selected_cell[COLOR_INDEX] == 0:
                        selected_cell[STATUS_FLOOR] = CELL_UNKNOWN
                        if (cell_x, cell_y) in self.workspace.memory.allocentric_memory.user_cells:
                            self.workspace.memory.allocentric_memory.user_cells.remove((cell_x, cell_y))
                    else:
                        # Mark a FLOOR cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y, EXPERIENCE_FLOOR,
                                                                                      self.workspace.memory.clock, 0)
                        self.workspace.memory.allocentric_memory.user_cells.append((cell_x, cell_y))
                # ALT: Toggle ECHO
                elif modifiers & key.MOD_ALT:
                    if selected_cell[STATUS_ECHO] == EXPERIENCE_ALIGNED_ECHO:
                        selected_cell[STATUS_ECHO] = CELL_UNKNOWN
                        selected_cell[COLOR_INDEX] = 0
                        if (cell_x, cell_y) in self.workspace.memory.allocentric_memory.user_cells:
                            self.workspace.memory.allocentric_memory.user_cells.remove((cell_x, cell_y))
                    else:
                        # Mark an echo cell
                        self.workspace.memory.allocentric_memory.apply_status_to_cell(cell_x, cell_y,
                                                                                      EXPERIENCE_ALIGNED_ECHO,
                                                                                      self.workspace.memory.clock, 0)
                        self.workspace.memory.allocentric_memory.user_cells.append((cell_x, cell_y))
                # No modifier: move the prompt
                else:
                    # Mark the prompt
                    self.workspace.memory.allocentric_memory.update_prompt(click_point, self.workspace.memory.clock)
                    # Store the prompt in egocentric memory
                    ego_point = self.workspace.memory.allocentric_to_egocentric(click_point)
                    self.workspace.memory.egocentric_memory.prompt_point = ego_point

                self.update_view()

            # Display this phenomenon in phenomenon window
            # if self.workspace.memory.allocentric_memory.grid[cell_x][cell_y][PHENOMENON_ID] != -1:
            #     self.workspace.ctrl_phenomenon_view.view.set_caption(f"Phenomenon {self.workspace.memory.allocentric_memory.grid[cell_x][cell_y][PHENOMENON_ID]}")
            #     self.workspace.ctrl_phenomenon_view.phenomenon_id = self.workspace.memory.allocentric_memory.grid[cell_x][cell_y][PHENOMENON_ID]
            #     self.workspace.ctrl_phenomenon_view.update_affordance_displays()

            # Display the grid cell status
            self.view.label2.text = f"Place {selected_cell[PLACE_CELL_ID]} " \
                                    f"Phen. {selected_cell[PHENOMENON_ID]} " \
                                    f"Update {selected_cell[CLOCK_UPDATED]} " \
                                    f"Status {tuple(selected_cell[STATUS_FLOOR: STATUS_4 + 1])} " \
                                    f"Clock {tuple(selected_cell[CLOCK_FOCUS:CLOCK_PLACE+1])} "

            # Display the place cell in place cell window
            self.workspace.show_place_cell(selected_cell[PLACE_CELL_ID])
            self.workspace.ctrl_place_cell_view.update_cue_displays()

        self.view.on_mouse_press = on_mouse_press

        def on_key_press(symbol, modifiers):
            """ Deleting the prompt"""
            if symbol == key.DELETE:
                self.delete_prompt()
                self.workspace.memory.allocentric_memory.user_cells = []

        self.view.on_key_press = on_key_press

    def delete_prompt(self):
        """Delete the prompt"""
        self.workspace.memory.egocentric_memory.prompt_point = None
        self.workspace.memory.allocentric_memory.update_prompt(None, self.workspace.memory.clock)
        self.update_view()

    def update_view(self):
        """Update the allocentric view from the status in the allocentric grid cells"""
        start_time = time.time()
        # Select the cells that have been updated during the max durability lapse
        # updated_ij = np.where(self.workspace.memory.allocentric_memory.grid[:, :, STATUS_0:CLOCK_PLACE+1] != 0)
        updated_ij = np.where((self.workspace.memory.allocentric_memory.grid[:, :, CLOCK_UPDATED]
                               >= self.workspace.memory.clock - PLACE_GRID_DURABILITY) & (
                              (self.workspace.memory.allocentric_memory.grid[:, :, STATUS_FLOOR] != 0)
                              | (self.workspace.memory.allocentric_memory.grid[:, :, STATUS_ECHO] != 0)
                              | (self.workspace.memory.allocentric_memory.grid[:, :, STATUS_2] != 0)
                              | (self.workspace.memory.allocentric_memory.grid[:, :, STATUS_3] != 0)
                              | (self.workspace.memory.allocentric_memory.grid[:, :, CLOCK_FOCUS] >=
                                 self.workspace.memory.clock - PLACE_GRID_DURABILITY)
                              | (self.workspace.memory.allocentric_memory.grid[:, :, CLOCK_PROMPT] >=
                                 self.workspace.memory.clock - PLACE_GRID_DURABILITY)))
        for i, j in zip(updated_ij[0], updated_ij[1]):
            self.view.update_hexagon(i, j, self.workspace.memory.allocentric_memory.grid[i][j][:],
                                     self.workspace.memory.clock)
        # print(f"Update alloview: {len(updated_ij[0])} cells in {time.time() - start_time:.3f} seconds")

        # Update the other robot
        # if ROBOT1 in self.workspace.memory.phenomenon_memory.phenomena:
        #     self.view.update_robot_poi(self.workspace.memory.phenomenon_memory.phenomena[ROBOT1])

    def main(self, dt):
        """Refresh allocentric view"""
        # The head and the LED color
        self.view.update_body_display(self.workspace.memory.body_memory)
        # The position of the robot in the view
        self.view.robot_rotate = 90 - self.workspace.memory.body_memory.body_azimuth()
        self.view.robot_translate = self.workspace.memory.allocentric_memory.robot_point
        # Refresh during the enaction and at the end of the interaction cycle
        if self.workspace.enacter.interaction_step in [ENACTION_STEP_ENACTING, ENACTION_STEP_RENDERING]:
            self.update_view()
