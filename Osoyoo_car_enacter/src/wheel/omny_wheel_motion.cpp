/*
 *  _____     _____     __      __   __     __   _______   __               _______         __         ___        ____   ______     __       ___
 * |  __  \  |  __  \  |  |    |  | |  \   |  | |   ____| |  |            /   _____|      /    \      |   \      /    | |   __  \  |  |    /     \
 * | |__|  | | |__|  | |  |    |  | |   \  |  | |  |__    |  |           /   /           /  /\  \     |    \    /     | |  |__|  | |  |   /   _   \
 * |     _/  |     _/  |  |    |  | |    \ |  | |     |   |  |          |   |  ____     /  /__\  \    |  |\  \ /  /|  | |  _____/  |  |  |   |  |  |
 * |  __  \  |  __  \  |  |    |  | |  |\ \|  | |   __|   |  |          |   |  |__ |   /   ____   \   |  |  \___/  |  | |  |       |  |  |   |_ |  |
 * | |__|  | | |  \  \ |   \__/   | |  | \    | |  |____  |  |____       \  \ _ |  |  /   /    \   \  |  |         |  | |  |       |  |   \       / 
 * |______/  |_|   \__\ \________/  |__|  \___| |_______| |_______|       \ _______| /__ /      \   \ |__|         |__| |__|       |__|    \ ___ /
 */


#include "omny_wheel_motion.h"
#include "Arduino.h"

//Controle de la vitesse des roues du robot
void setMotion(int speed_fl,int speed_rl ,int speed_rr,int speed_fr)
{
   FL(speed_fl);
   RL(speed_rl);
   FR(speed_fr);
   RR(speed_rr);
}

void go_forward(int speed) // faire avancer le robot
{
  setMotion(speed,speed,speed,speed);
}
void  go_back(int speed)//faire reculer le robot 
{
  setMotion(-speed,-speed,-speed,-speed);
}

void right_turn(int speed)//Faire tourne le robot à droite 
{
   setMotion(speed,speed,0,0);
}

void left_turn(int speed)//Faire tourne le robot à gauche 
{
    setMotion(0,0,speed,speed);
}

void FL(int speed)  //Rotation de la roue avant gauche 
{
  if(speed > 0)
  {
      digitalWrite(LeftMotorDirPin1,LOW);
      digitalWrite(LeftMotorDirPin2,HIGH);
      analogWrite(speedPinL,speed);
  }
  else 
  {
      digitalWrite(LeftMotorDirPin1,HIGH);
      digitalWrite(LeftMotorDirPin2,LOW);
      analogWrite(speedPinL,-speed);
  }
}
void RR(int speed)  //Rotation de la roue arriere droit  
{
  if(speed > 0)
  {
      digitalWrite(RightMotorDirPin1B, LOW);
      digitalWrite(RightMotorDirPin2B,HIGH); 
      analogWrite(speedPinRB,speed);
  }
  else
  { 
      digitalWrite(RightMotorDirPin1B, HIGH);
      digitalWrite(RightMotorDirPin2B,LOW); 
      analogWrite(speedPinRB,-speed);
  }
}
void FR(int speed) //Rotation de la roue avant droit 
{
  if(speed > 0){
      digitalWrite(RightMotorDirPin1, LOW);
      digitalWrite(RightMotorDirPin2,HIGH); 
      analogWrite(speedPinR,speed);
  }
  else{
      digitalWrite(RightMotorDirPin1,HIGH);
      digitalWrite(RightMotorDirPin2,LOW); 
      analogWrite(speedPinR,-speed);
  }
}
void RL(int speed)//Rotation de la roue arriere gauche 
{
    if(speed > 0)
    {
        digitalWrite(LeftMotorDirPin1B,LOW);
        digitalWrite(LeftMotorDirPin2B,HIGH);
        //Ajout de la puissance supplementaire de 1.2 à la roue pour cause de defaillance
        analogWrite(speedPinLB,1.2*speed);
    }
    else
    {
        digitalWrite(LeftMotorDirPin1B,HIGH);
        digitalWrite(LeftMotorDirPin2B,LOW);
        analogWrite(speedPinLB,-speed*1.2);
    }
}

//Arret moteur lors de l'appel de la fonction
void stop_Stop()    //Stop
{
  analogWrite(speedPinLB,0);
  analogWrite(speedPinRB,0);
  analogWrite(speedPinL,0);
  analogWrite(speedPinR,0);
}
