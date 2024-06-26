/*
  Head_echo_alignment.h - library for Osoyoo car align head towards closest ultrasonic echo.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#include "Arduino.h"
#include "Robot_define.h"
#include "Head.h"
#include <Servo.h>

Head::Head()
{
}

void Head::setup()
{
  // init HC-SR04 ultrasonic Echo sensor
  pinMode(Trig_PIN, OUTPUT);
  pinMode(Echo_PIN,INPUT);
  digitalWrite(Trig_PIN,LOW);
  // init servo
  _head.attach(SERVO_PIN);
  turnHead(0); // Head straight ahead
  _head_angle_span = ALIGN_SACCADE_SPAN;
}

void Head::beginEchoAlignment()
{
  _is_enacting_head_alignment = true;
  // Reinitialize the previous measures because we don't know where they were taken
  _previous_ultrasonic_measure  = NO_ECHO_DISTANCE;
  _current_ultrasonic_measure = NO_ECHO_DISTANCE;
  // Inverse the movement to track moving objects more easily
  _head_angle_span = - _head_angle_span;
  _echo_alignment_step = 0;
  _next_saccade_time = millis() + SACCADE_DURATION;
}

void Head::update()
{
  if (millis() > _next_saccade_time )
  {
    _penultimate_ultrasonic_measure = _previous_ultrasonic_measure;
    _previous_ultrasonic_measure = _current_ultrasonic_measure;
    _current_ultrasonic_measure = measureUltrasonicEcho();

    if (_is_enacting_head_alignment)
    {
      _echo_alignment_step++;
      _next_saccade_time = millis() + SACCADE_DURATION;

      // Check the variation from the last saccade below  660mm/s.
      if (abs(_current_ultrasonic_measure - _previous_ultrasonic_measure) > ECHO_MONITOR_VARIATION * 2 &&
          abs(_current_ultrasonic_measure - _penultimate_ultrasonic_measure) > ECHO_MONITOR_VARIATION * 2) // &&
          // abs(_current_ultrasonic_measure - _previous_ultrasonic_measure) < 9000 )
        {
          _discontinuous = true;
          //Serial.print("Discontinuous: "); Serial.print(_current_ultrasonic_measure);
          //Serial.print(" "); Serial.println(_previous_ultrasonic_measure);
        }
      //Serial.print("Step: "); Serial.print(_echo_alignment_step);
      //Serial.print(", Angle: "); Serial.print(_head_angle);
      //Serial.print(", measure: "); Serial.println(_current_ultrasonic_measure);

      // If the echo is closer than the previous or no current echo and no previous and no penultimate
      if ((_current_ultrasonic_measure < _previous_ultrasonic_measure ) ||
          ( _current_ultrasonic_measure == NO_ECHO_DISTANCE)
           && ( _previous_ultrasonic_measure == NO_ECHO_DISTANCE)
           && (_penultimate_ultrasonic_measure == NO_ECHO_DISTANCE))
      {
        if ((_head_angle <= -90) || (_head_angle >= 90))
        // The head reached the limit angle
        {
          if (_echo_alignment_step > 1)
          // The echo is closer after several steps then the min distance is on the limit angle
          {
            _min_ultrasonic_measure = _current_ultrasonic_measure;
            //Serial.print("Aligned at limit angle: "); Serial.print(_head_angle);
            //Serial.print(", measure "); Serial.println(_min_ultrasonic_measure);
            _is_enacting_head_alignment = false;
            _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Wait before monitoring again
          }
          else
          // First step on the limit angle: apply the saccade towards the center
          {
            _head_angle_span = ALIGN_SACCADE_SPAN;
            if (_head_angle >= 90)
              _head_angle_span = -ALIGN_SACCADE_SPAN;
            _head_angle += _head_angle_span;
            turnHead(_head_angle);
          }
        }
        else
          // The head did not reach the limit angle, the head must continues in the same direction
          turnHead(_head_angle += _head_angle_span);
      }

      // The current echo is farther than or equal to the previous echo or both don't exist but the penultimate exists
      else
      {
        // Reverse the head direction to go back to the previous position
        _head_angle_span = - _head_angle_span;
        _head_angle += _head_angle_span;
        turnHead(_head_angle);
        // If the penultimate echo is farther than or equal to the previous then stop the alignment
        // unless the current and the previous measure returned no echo
        if ((_penultimate_ultrasonic_measure >= _previous_ultrasonic_measure) &&  (_echo_alignment_step >= 2)
            &&  (_previous_ultrasonic_measure < NO_ECHO_DISTANCE))
        {
          _min_ultrasonic_measure = _previous_ultrasonic_measure;
          //Serial.print("Aligned at angle: "); Serial.print(_head_angle);
          //Serial.print(", measure "); Serial.println(_min_ultrasonic_measure);
          _is_enacting_head_alignment = false;
          _next_saccade_time = millis() + ECHO_MONITOR_PERIOD; // Switch to monitoring period
        }
      }
    }
    else
    // Watch out for variation in ultrasonic measure to trigger alignment
    {
      _next_saccade_time = millis() + ECHO_MONITOR_PERIOD;
      // If the difference from the min aligned measure over two cycles is greater then monitoring distance
      if (abs(_current_ultrasonic_measure  - _min_ultrasonic_measure) > ECHO_MONITOR_VARIATION &&
          abs(_previous_ultrasonic_measure - _min_ultrasonic_measure) > ECHO_MONITOR_VARIATION)
      {
        //Serial.print("Trigger alignment from Angle: "); Serial.print(_head_angle);
        //Serial.print(", measure: "); Serial.print(_current_ultrasonic_measure);
        //Serial.print(", variation: "); Serial.println(_current_ultrasonic_measure - _min_ultrasonic_measure);
        beginEchoAlignment();
      }
    }
  }
}

// Return the last ultrasonic measure
int Head::get_ultrasonic_measure()
{
  return _current_ultrasonic_measure;
}

void Head::outcome(JSONVar & outcome_object)
{
  outcome_object["head_angle"] = _head_angle;

  // The latest measure obtained from echo alignment
  if (_min_ultrasonic_measure < NO_ECHO_DISTANCE)
    outcome_object["echo_distance"] = _min_ultrasonic_measure;
}

void Head::turnHead(int head_angle)
{
  _head_angle = constrain(head_angle, -90, 90);
  // Serial.print("Turning head to: "); Serial.println(_head_angle);
  _head.write(_head_angle + 90);
}

int Head::measureUltrasonicEcho()
{
  long echo_distance;
  digitalWrite(Trig_PIN,LOW);
  delayMicroseconds(5);
  digitalWrite(Trig_PIN,HIGH);
  delayMicroseconds(15);
  digitalWrite(Trig_PIN,LOW);
  echo_distance = pulseIn(Echo_PIN,HIGH, 10000);  // Timeout 10 milliseconds, otherwise it blocks the main loop!
  echo_distance = (int)(echo_distance * 0.1657);  // Convert to mm
  if (echo_distance == 0) echo_distance = NO_ECHO_DISTANCE;  // Zero counts for no echo
  //Serial.println("Angle " +String(_head_angle) + " measure " + String(echo_distance));
  return echo_distance;
}

// Return the head direction toward the (x,y) point
int Head::head_direction(int x, int y)
{
  if (x < ROBOT_HEAD_X)
  {
    // The focus is behind the head
    if (y > 0)
      return 90;
    else if (y < 0)
      return -90;
    else
      return 0;
  }
  else
    // The focus is before the head
    return (int)(atan2(y, x-ROBOT_HEAD_X) * 180.0 / M_PI);
}
