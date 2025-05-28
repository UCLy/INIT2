#define ROBOT_ID 2 // 0: Default Osoyoo robot, 1: robot BSN, 2: robot UCBL, 3: SHS chez Olivier, 11 to 14: DOLL robots

#define AP_SSID "Petitcat"              // The wifi SSID of this robot in Access Point
#define ROBOT_HEAD_X 80                 // (mm) X position of the head
#define SPEED 120                       // motor control
#define TURN_SPEED 110                  // (degree/s)
#define SHIFT_SPEED 150                 // motor control 130
#define TURN_TIME 500                   // (ms)
#define MOVE_TIME 500                   // (ms)
#define TURN_SPOT_ANGLE 45              // (degree)
#define WHITE_RED 100.                  // Color sensor calibration red measure of white floor
#define WHITE_GREEN 100.                // Color sensor calibration green measure of white floor
#define WHITE_BLUE 100.                 // Color sensor calibration blue measure of white floor

#define TOUCH_PIN 52

#if ROBOT_ID == 1

#warning "Compiling for BSN's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2 // "MMC5883"
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1.2
#define FRONT_RIGHT_WHEEL_COEF 1.2
#define FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 400  // 500
#define TURN_SPOT_ENDING_ANGLE 18  // 20  //  25
#define ACCELERATION_X_OFFSET -15  // -40
#define ACCELERATION_Y_OFFSET -30  // -3
#define COMPASS_X_OFFSET 6982 // 7062 // 7051 // 7022
#define COMPASS_Y_OFFSET 7320  // 7306 // 7336
#define ACCELERATION_X_IMPACT_THRESHOLD 250 // 200 // -400 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_Y_IMPACT_THRESHOLD 200 //  110
#define ACCELERATION_X_BLOCK_THRESHOLD 60  // TODO depends whether the interaction starts when the robot is immobile
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // 100 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 0.97  // 1.2  //  1 // IMU is upright. If turns too much, increase this value
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define WHITE_RED 67.
#define WHITE_GREEN 103.
#define WHITE_BLUE 91.
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 5
#define SERVO_PIN 6  // 13 Changed because 13 is used for built-in led
#define RightMotorDirPin1B 23  // 5 Changed because we use 5 for Emotion LED
#define RightMotorDirPin2B 25  // 5 Changed because we use 6 for Emotion LED

#elif ROBOT_ID == 2

#warning "Compiling for Olivier's robot"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE  1 // "HMC5883L"
#define REAR_RIGHT_WHEEL_COEF 1.1  // 1.1
#define REAR_LEFT_WHEEL_COEF 1 // 1
#define FRONT_RIGHT_WHEEL_COEF 0.9  //1
#define FRONT_LEFT_WHEEL_COEF 1  // 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200  // Rotation speed is about 1° per 10ms
#define TURN_SPOT_ENDING_ANGLE 10
#define COMPASS_X_OFFSET 858 // 651  // 1089      // Previous IMU board: 1421
#define COMPASS_Y_OFFSET -1272  // -987 // -1547     // Previous IMU board: -1601
#define ACCELERATION_X_OFFSET 0    // Previous IMU board: -550
#define ACCELERATION_Y_OFFSET -35  // Previous IMU board: 150
#define ACCELERATION_X_IMPACT_THRESHOLD 250 // -400 // Below the threshold it is a strong deceleration = shock
#define ACCELERATION_Y_IMPACT_THRESHOLD 200
#define ACCELERATION_X_BLOCK_THRESHOLD 60 // Below the threshold, the robot is blocked
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 0.99  // 1.0
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define WHITE_RED 70.
#define WHITE_GREEN 91.
#define WHITE_BLUE 77.
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 5
#define SERVO_PIN 6
#define RightMotorDirPin1B 23
#define RightMotorDirPin2B 25

#elif ROBOT_ID == 3

#warning "Compiling for SHS's robot with GY-86"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1 //  "HMC5883L"
#define REAR_LEFT_WHEEL_COEF  1.2  // 1.1 20/05/2023 // 1.3 04/04/2023 // 1.1 26/02/2023 // 1
#define FRONT_LEFT_WHEEL_COEF 1.2  // 1.1 20/05/2023 // 1.3 04/04/2023
#define REAR_RIGHT_WHEEL_COEF 1.0  //                                     0.9 26/02/2023
#define FRONT_RIGHT_WHEEL_COEF 1.0 // 1.1 20/05/2023 // 1.0 04/04/2023 // 1.1 26/02/2023 // 1.2 29/05/2022
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 150 // 200
#define TURN_SPOT_ENDING_ANGLE 6 // 9 // 5
#define COMPASS_X_OFFSET  870  // 1071  // 1100  // 1005  //  1020,  1060
#define COMPASS_Y_OFFSET  -1000 // -1225  // -1300  // -1247 // -1300, -1290
#define ACCELERATION_X_OFFSET -55  // 55  // 35
#define ACCELERATION_Y_OFFSET 0  // -3        //
#define ACCELERATION_X_IMPACT_THRESHOLD 210  // 200 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 110  // 140 // 30 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // 100 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.
#define GYRO_IMPACT_THRESHOLD 0.5 // 0.25      // (degree/s) above this threshold: strong z rotation = lateral impact
#define WHITE_RED 69.
#define WHITE_GREEN 107.
#define WHITE_BLUE 94.
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 5
#define SERVO_PIN 6
#define RightMotorDirPin1B 23
#define RightMotorDirPin2B 25

#elif ROBOT_ID == 4

#warning "Compiling for Robot 4"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1 //  "HMC5883L"
#define REAR_LEFT_WHEEL_COEF  0.6
#define FRONT_LEFT_WHEEL_COEF 0.6
#define REAR_RIGHT_WHEEL_COEF 0.6
#define FRONT_RIGHT_WHEEL_COEF 0.6
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 180  // 200 // 400 for WHEEL_COEFs 0.8
#define TURN_SPOT_ENDING_ANGLE 9 // 10  // 18
#define COMPASS_X_OFFSET  205  // 155  // 163
#define COMPASS_Y_OFFSET  -105  // -554  // -665
#define ACCELERATION_X_OFFSET -30
#define ACCELERATION_Y_OFFSET 0
#define ACCELERATION_X_IMPACT_THRESHOLD 250
#define ACCELERATION_Y_IMPACT_THRESHOLD 250
#define ACCELERATION_X_BLOCK_THRESHOLD 140
#define ACCELERATION_Y_BLOCK_THRESHOLD 80
#define GYRO_COEF 0.98  // If average(integrated_yaw - compass)>0 when turning trigonometric (left "1") then decrease this value
#define GYRO_IMPACT_THRESHOLD 0.5
#define WHITE_RED 89.
#define WHITE_GREEN 93.
#define WHITE_BLUE 89.
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 5
#define SERVO_PIN 6
#define RightMotorDirPin1B 23
#define RightMotorDirPin2B 25

#elif ROBOT_ID == 11

#warning "Compiling for DOLL robot D1"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 1 // "HMC5883L"
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1
#define FRONT_RIGHT_WHEEL_COEF 1
#define FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET -936  // -1155
#define COMPASS_Y_OFFSET -931  // -1150
// #define ACCELERATION_IMPACT_THRESHOLD -300
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 3  // Not used yet
#define SERVO_PIN 4
#define RightMotorDirPin1B 5
#define RightMotorDirPin2B 6

#elif ROBOT_ID == 12

#warning "Compiling for DOLL robot D2"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2// "MMC5883"
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1
#define FRONT_RIGHT_WHEEL_COEF 1
#define FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 6435
#define COMPASS_Y_OFFSET 5581
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 3  // Not used yet
#define SERVO_PIN 4
#define RightMotorDirPin1B 5
#define RightMotorDirPin2B 6

#elif ROBOT_ID == 13

#warning "Compiling for DOLL robot D3"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1
#define FRONT_RIGHT_WHEEL_COEF 1
#define FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 15
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 6021
#define COMPASS_Y_OFFSET 5653
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.4
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 3  // Not used yet
#define SERVO_PIN 4
#define RightMotorDirPin1B 5
#define RightMotorDirPin2B 6

#elif ROBOT_ID == 14

#warning "Compiling for DOLL robot D4"
#define ROBOT_HAS_MPU6050  true
#define ROBOT_COMPASS_TYPE 2
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1
#define FRONT_RIGHT_WHEEL_COEF 1
#define FRONT_LEFT_WHEEL_COEF 1.2
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 200
#define TURN_SPOT_ENDING_ANGLE 10
#define ACCELERATION_X_OFFSET 0
#define ACCELERATION_Y_OFFSET 0
#define COMPASS_X_OFFSET 5921
#define COMPASS_Y_OFFSET 5669
#define ACCELERATION_X_IMPACT_THRESHOLD 200  // 300 Longitudinal impact if acceleration exceeds this threshold
#define ACCELERATION_Y_IMPACT_THRESHOLD 200  // 110 lateral impact if acceleration exceeds this threshold
#define ACCELERATION_X_BLOCK_THRESHOLD 140 // 50 // Robot is blocked if longitudinal acceleration below this threshold
#define ACCELERATION_Y_BLOCK_THRESHOLD 80 // Robot is blocked if lateral acceleration below this threshold
#define GYRO_COEF 1.  // 1.5
#define GYRO_IMPACT_THRESHOLD 0.25      // (degree) above this threshold: strong z rotation = lateral impact
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 3  // Not used yet
#define SERVO_PIN 4
#define RightMotorDirPin1B 5
#define RightMotorDirPin2B 6


#else

#warning "Compiling for a regular Osoyoo robot"
#define ROBOT_HAS_MPU6050 false
#define REAR_RIGHT_WHEEL_COEF 1
#define REAR_LEFT_WHEEL_COEF 1
#define FRONT_RIGHT_WHEEL_COEF 1
#define FRONT_LEFT_WHEEL_COEF 1
#define TURN_SPOT_MAX_DURATION 2400
#define TURN_SPOT_ENDING_DELAY 180
#define TURN_SPOT_ENDING_ANGLE 9
#define BLUE_LED_PIN 2
#define GREEN_LED_PIN 3
#define RED_LED_PIN 3  // Not used yet
#define RightMotorDirPin1B 5  // Rear Right Motor direction pin 1 to Back MODEL-X IN1 (K1)
#define RightMotorDirPin2B 6   // Rear Right Motor direction pin 2 to Back MODEL-X IN2 (K1)
#define SERVO_PIN 13

#endif
