
# Olivier's robot:
#   7V: 160 mm
#   8V: 190 mm
#

CHECK_OUTSIDE = 0           # 1 if robot checks echos outside terrain

ROBOT_COLOR_SENSOR_X = 50   # (mm) The X position of the color sensor
ROBOT_HEAD_X = 80           # (mm) The X position of the head pivot
ROBOT_CHASSIS_X = 100       # (mm) The X position of the robot front chassis
ROBOT_FLOOR_SENSOR_X = 110  # (mm) The X position of the robot floor sensor
ROBOT_CHASSIS_Y = 80        # (mm) The Y position of the robot front to mark lateral shocks
ROBOT_OUTSIDE_Y = 120       # (mm) The Y position of the outside border of the robot

DEFAULT_YAW = 45                  # (degree) Default rotation when yaw is not returned by the robot
DEFAULT_ACTION_DURATION = 1000    # (ms) The default duration of actions (value of Interaction.h/_target_duration )
# RETREAT_DISTANCE_Y = 20  # 75     # (mm) Y displacement when line is detected on the side

TERRAIN_RADIUS = {"0": {"radius": 650, "short_radius": 650, "azimuth": 90},
                  "BSN": {"radius": 1100, "azimuth": 25, "short_radius": 800},  #  25 990 x 600  45},
                  "Circle": {"radius": 650, "short_radius": 650, "azimuth": 90},  # Petit tapis
                  "PetiteIA": {"radius": 1100, "azimuth": 55, "short_radius": 650},  # {990, 60},  # Grand tapis
                  "A301": {"radius": 1200, "azimuth": 50},
                  "DOLL": {"radius": 1200, "azimuth": 0, "short_radius": 1000},      # To be defined
                  "AP": {"radius": 1200, "azimuth": 0, "short_radius": 1000},  # To be defined
                  "lowcal": {"radius": 1200, "azimuth": 0, "short_radius": 1000}  # To be defined
                  }

ROBOT_SETTINGS_0 = {
    "IP": {},
    "forward_speed": 300,  # (mm/s) Forward translation speed.
    "lateral_speed": 140,  # (mm/s) Lateral translation speed.
    "retreat_distance": [90, 30, 0],  # (mm) Distance of the line after retreat
    "retreat_yaw": 30,  # (degree) Yaw after retreat. IWAI paper: 40 to show calibration
    "compass_offset": [0, 0, 0]  # Compass offset can also be added into the C++ code.
    }

# Robot 1 in Lyon.
ROBOT_SETTINGS_1 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_1["IP"] = {"A328": "192.168.8.230", "PetiteIA": "192.168.8.0", "AP": "192.168.4.1"}
ROBOT_SETTINGS_1["forward_speed"] = 300  # (mm/s) Forward translation speed.
ROBOT_SETTINGS_1["lateral_speed"] = 260  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_1["retreat_distance"] = [90, 30, 0]   # (mm) Distance of the line after retreat
ROBOT_SETTINGS_1["compass_offset"] = [57, 21, 0]  # [0, 0, 0]  # Compass offset can also be added into the C++ code.

# Robot 2 in Lyon.
ROBOT_SETTINGS_2 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_2["IP"] = {"BSN": "192.168.8.189", "PetiteIA": "192.168.8.189", "AP": "192.168.4.1"}
ROBOT_SETTINGS_2["forward_speed"] = 230  # (mm/s) Forward translation speed.
ROBOT_SETTINGS_2["lateral_speed"] = 140  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_2["retreat_distance"] = [90, 30, 0]
ROBOT_SETTINGS_2["compass_offset"] = [-70, 0, 0]  # [0, 0, 0]  # [-30, 40, 0]

# Robot 3 chez Olivier
ROBOT_SETTINGS_3 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_3["IP"] = {"lowcal": "192.168.10.104", "A301": "192.168.8.242", "PetiteIA": "192.168.8.108"}  # 242
# Lower speed cause the robot to believe the arena is smaller. Reduce speed to prevent pushing outside objects
ROBOT_SETTINGS_3["forward_speed"] = 190  # 260  # 230  190 (mm/s) Forward translation speed.
ROBOT_SETTINGS_3["lateral_speed"] = 130  # 170  # 230  160  # (mm/s) Lateral translation speed.
ROBOT_SETTINGS_3["retreat_distance"] = [90, 30, 0]
ROBOT_SETTINGS_3["compass_offset"] = [0, 0, 0]  # [-50, 0, 0] [50, -50, 0]  # [30, -20, 0]  # [-40, 7, 0]  # [-30, 40, 0]

# Robot 4 chez Olivier
ROBOT_SETTINGS_4 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_4["IP"] = {"PetiteIA": "192.168.8.242", "Circle": "192.168.8.242"}  # 108
# ROBOT_SETTINGS_4["IP"] = {"PetiteIA": "192.168.8.242", "Circle": "192.168.4.1"}  # 108
ROBOT_SETTINGS_4["forward_speed"] = 300  # 320
ROBOT_SETTINGS_4["lateral_speed"] = 200  # 50
ROBOT_SETTINGS_4["retreat_distance"] = [120, 50, 0]  # Increase if the line keeps being pushed farther
ROBOT_SETTINGS_4["compass_offset"] = [0, 0, 0]  # [33, -5, 0]  # [50, -5, 0]  # [76, 0, 0]

# Robot 1 at DOLL
ROBOT_SETTINGS_11 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_11["IP"] = {"DOLL": "192.168.11.161"}
ROBOT_SETTINGS_11["forward_speed"] = 290
ROBOT_SETTINGS_11["compass_offset"] = [0, 0, 0]

# Robot 2 at DOLL
ROBOT_SETTINGS_12 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_12["IP"] = {"DOLL": "192.168.11.174"}
ROBOT_SETTINGS_12["forward_speed"] = 260

# Robot 3 at DOLL
ROBOT_SETTINGS_13 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_13["IP"] = {"DOLL": "192.168.11.197"}
ROBOT_SETTINGS_13["forward_speed"] = 290

# Robot 4 at DOLL
ROBOT_SETTINGS_14 = ROBOT_SETTINGS_0.copy()
ROBOT_SETTINGS_14["IP"] = {"DOLL": "192.168.11.184"}
ROBOT_SETTINGS_14["forward_speed"] = 210

ROBOT_SETTINGS = {
    '0': ROBOT_SETTINGS_0,
    '1': ROBOT_SETTINGS_1,
    '2': ROBOT_SETTINGS_2,
    '3': ROBOT_SETTINGS_3,
    '4': ROBOT_SETTINGS_4,
    '11': ROBOT_SETTINGS_11,
    '12': ROBOT_SETTINGS_12,
    '13': ROBOT_SETTINGS_13,
    '14': ROBOT_SETTINGS_14,
    }
