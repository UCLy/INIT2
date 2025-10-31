#!/usr/bin/env python
# Olivier Georgeon, 2025.
# This code is used to tele-operate the robot from input prompts.

import socket
import sys
import json

UDP_IP = "192.168.4.1"
UDP_TIMEOUT = 5  # Seconds


class PromptTeleop:
    def __init__(self, ip, time_out, port=8888):
        self.IP = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(time_out)
        self.clock = 0
        self.focus_x = None
        self.focus_y = None
        self.color = None
        self.duration = None
        self.angle = None
        self.span = None

    def send_command(self, command_string):
        """ Sending the action string, waiting for the outcome, and returning the outcome bytes """
        _outcome = None  # Default if timeout
        # print("sending ", action, "to", (self.IP, self.port), "...")
        try:
            self.socket.sendto(bytes(command_string, 'utf-8'), (self.IP, self.port))
            _outcome, address = self.socket.recvfrom(512)
        except socket.gaierror:  # Invalid IP address
            print("Invalid IP address: ", self.IP)
        except socket.error as error:  # Time out error when robot is not connected
            print(error)
        return _outcome

    def send(self, _action):
        """Format the action string for the notebook"""
        command_dict = {'clock': self.clock, 'action': _action}
        if self.focus_x is not None:
            command_dict['focus_x'] = self.focus_x
        if self.focus_y is not None:
            command_dict['focus_y'] = self.focus_y
        if self.color is not None:
            command_dict['color'] = self.color
        if self.duration is not None:
            command_dict['duration'] = self.duration
        if self.angle is not None:
            command_dict['angle'] = self.angle
        _action_string = json.dumps(command_dict)
        print("Sending packet:", _action_string)
        _outcome = self.send_command(_action_string)
        print("Received packet:", _outcome)
        if _outcome is not None:
            self.clock += 1
        print("Next clock:", self.clock)
        return _outcome


def usage():
    print("Action keys: 1: Turn left, 2: Backward, 3: Turn right, 4: Swipe left, 6: Swipe right, 8: Forward, -: Scan")


# Test the wifi interface by controlling the robot from the console
# Provide the Robot's IP address as a launch argument. For example:
# py prompt_teleop.py 192.168.8.242
if __name__ == '__main__':
    robot_ip = UDP_IP
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    else:
        robot_ip = input(f"Please provide your robot's IP address or press ENTER for default {UDP_IP} : ")
        if robot_ip == "":
            robot_ip = UDP_IP

    print("Connecting to robot: " + robot_ip)
    usage()
    teleop = PromptTeleop(robot_ip, UDP_TIMEOUT)
    clock = 0
    action = ""
    while True:
        action = input("Enter action key:")
        action_string = '{"clock":' + str(clock) + ', "action":"' + action + '"}'
        print("Sending packet:", action_string)
        outcome = teleop.send_command(action_string)
        print("Received packet:", outcome)
        if outcome is not None:
            outcome_dict = json.loads(outcome)
            if outcome_dict.get("status") == "Unknown":
                print("Unknown command. Please choose from:")
                usage()
            else:
                clock += 1
