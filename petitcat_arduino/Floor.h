/*
  Floor_change_retreat.h - library for Osoyoo car enacting floor change retreat behavior.
  Created by Olivier Georgeon, june 20 2021
  released into the public domain
*/
#ifndef Floor_h
#define Floor_h

#include "Arduino.h"
#include "Wheel.h"
#include "Color.h"
#include <Arduino_JSON.h>

#define RETREAT_DURATION 200
#define RETREAT_EXTRA_DURATION 100

class Floor
{
  public:
    Floor();
    void setup();
    int update(int interaction_direction);
    int measureFloor();
    void extraDuration(int duration);
    void outcome(JSONVar & outcome_object);
    bool _is_retreating = false;
    unsigned long _retreat_end_time = 0;
    Wheel _OWM;  // Omni-Wheel Motion
    Color _CLR;
    int _floor_outcome = 0;  // Create a begin() and move this to private?
  private:
    int _previous_measure_floor = 0;
};

#endif