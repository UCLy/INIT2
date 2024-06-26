/*
  Wheel.h - library for Osoyoo car motion command.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Wheel_h
#define Wheel_h
#include "Arduino.h"

#define speedPinR 9            // RIGHT WHEEL PWM pin D45 connect front MODEL-X ENA
#define RightMotorDirPin1  22  // Front Right Motor direction pin 1 to Front MODEL-X IN1 (K1)
#define RightMotorDirPin2  24  // Front Right Motor direction pin 2 to Front MODEL-X IN2 (K1)
#define LeftMotorDirPin1  26   // Left  front Motor direction pin 1 to Front MODEL-X IN3 (K3)
#define LeftMotorDirPin2  28   // Left  front Motor direction pin 2 to Front MODEL-X IN4 (K3)
#define speedPinL 10           // LEFT  WHEEL PWM pin D7 connect front MODEL-X ENB

#define speedPinRB 11          // RIGHT WHEEL PWM pin connect Back MODEL-X ENA
//#define RightMotorDirPin1B 5 // Was moved to Robot_define.h
//#define RightMotorDirPin2B 6 // Was moved to Robot_define.h
#define LeftMotorDirPin1B 7    // Rear  left Motor direction pin 1 to Back MODEL-X IN3  (K3)
#define LeftMotorDirPin2B 8    // Rear  left Motor direction pin 2 to Back MODEL-X IN4  (k3)
#define speedPinLB 12          // LEFT  WHEEL PWM pin D8 connect Rear MODEL-X ENB

class Wheel
{
  public:
    Wheel();
    void setup();
    void turnInSpotLeft(int speed);
    void goBack(int speed);
    void turnInSpotRight(int speed);
    void turnFrontLeft(int speed);
    void turnFrontRight(int speed);
    void shiftLeft(int speed);
    void shiftRight(int speed);
    void turnLeft(int speed);
    void goForward(int speed);
    void turnRight(int speed);
    void retreatRight();
    void retreatStrait();
    void retreatLeft();
    void retreatForward();
    void retreatLeftward();
    void retreatRightward();
    void stopMotion();
    void circumvent(int speed);
  // private:
    void setMotion(int speed_fl, int speed_rl, int speed_rr, int speed_fr);
    void frontLeftWheel(int speed);
    void rearLeftWheel(int speed);
    void frontRightWheel(int speed);
    void rearRightWheel(int speed);
};

#endif