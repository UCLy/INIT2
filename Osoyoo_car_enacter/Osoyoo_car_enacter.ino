/*
 * .______        _______..__   __.
 * |   _  \      /       ||  \ |  |
 * |  |_)  |    |   (----`|   \|  |
 * |   _  <      \   \    |  . `  |
 * |  |_)  | .----)   |   |  |\   |
 * |______/  |_______/    |__| \__|
 *
 *  BSN2 2021-2022
 *   Aleksei Apostolou, Daniel Duval, Célien Fiorelli, Geordi Gampio, Julina Matouassiloua
 *
 *  Teachers
 *   Raphaël Cazorla, Florian Tholin, Olivier Georgeon
 *
 *  Bachelor Sciences du Numerique. ESQESE. UCLy. France
 *
 * Warning: If libraries MPU6050_Light, MPU6050, and HMC5883L are not installed
 * and if the robot does not have an IMU board then please comment the corresponding code below
 */

#include "src/wheel/omny_wheel_motion.h"
#include "src/lightSensor/LightSensor.h"
LightSensor ls;
int previous_floor = 0; 


#define WifiMode "R"        // Define the wifi mode of the robot, 'R' for router and 'W' for robot connection

#include "src/imu/gyro.h"    // Comment if the robot has no IMU
#include "src/imu/compass.h" // Comment if the robot has no compass

#include "src/wifi/JsonOutcome.h"
JsonOutcome outcome;

#include "src/head/Head.h"
Head head;

#include "src/utils/DelayAction.h"
DelayAction da;

#include "src/wifi/WifiBot.h"
WifiBot wifiBot = WifiBot("osoyoo_robot2", 8888);

#include "WiFiEsp.h"
#include "WiFiEspUDP.h"

#include "Arduino_JSON.h"

// use a ring buffer to increase speed and reduce memory allocation
char packetBuffer[100];
char action = ' ';

unsigned long endTime = 0;
int actionStep = 0;
float somme_gyroZ = 0;
int floorOutcome = 0;

void setup()
{
  Serial.begin(9600);   // initialize serial for debugging
  
  head.servo_port();
  
  head.distUS.setup();
  if (WifiMode == "W"){

    wifiBot.wifiInitLocal();
  }
  if (WifiMode == "R"){
    wifiBot.wifiInitRouter();
  }

  compass_setup(); // Comment if the robot has no compass
  mpu_setup();     // Must be after compass_setup() otherwise yaw is distorted
}

void loop()
{
  da.checkDelayAction(millis());
  
  int packetSize = wifiBot.Udp.parsePacket();
  gyro_update();

  if (packetSize) { // if you get a client
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    int len = wifiBot.Udp.read(packetBuffer, 255);

    if (len > 0) {
      packetBuffer[len] = 0;
    }

    if (len == 1) { // If one character, then it is the action
        action = packetBuffer[0];
    } else {        // If more than one characters, then it is a JSon string
      JSONVar jsonReceive = JSON.parse(packetBuffer);
      if (jsonReceive.hasOwnProperty("action")) {
        action = ((const char*) jsonReceive["action"])[0];
      }
    }

    endTime = millis() + 2000;
    actionStep = 1;

    switch (action)    //serial control instructions
    {  
      case '8':go_forward(SPEED);break;
      case '1':left_turn(SPEED);break;
      case '3':right_turn(SPEED);break;
      case '2':go_back(SPEED);break;
      case '5':stop_Stop();break;
      case '0':ls.until_line(SPEED);break;
      case '-': head.scan(0, 180, 9, 0);break;
      default:break;
    }
  }
  
  int current_floor = ls.tracking();
  if (current_floor != previous_floor) // la fonction renvoie true si elle capte une ligne noir
  {
    stop_Stop();
    if (current_floor > 0)
    {
      floorOutcome = current_floor;
    }
    go_back(SPEED);
    actionStep = 1;
    endTime = millis() + 1000; // 1 sec

    previous_floor = current_floor;
  }
  
  if ((endTime < millis()) && (actionStep == 1))
  {
    stop_Stop();
    
    outcome.addInt("echo_distance", (int) head.distUS.dist());
    outcome.addInt("head_angle", (int) (head.current_angle -  90));
    outcome.addInt("floor", (int) floorOutcome);
    outcome.addInt("status", (int) floorOutcome);
    outcome.addInt("yaw", (int) (gyroZ()));
    outcome.addInt("azimuth", (int) (degreesNorth()));  // Comment if the robot as no compass

    //Send outcome to PC
    wifiBot.sendOutcome(outcome.get());
    outcome.clear();
    
    actionStep = 0;
    floorOutcome = 0;
    reset_gyroZ();
  }
}
