#ifndef gyro_h
#define gyro_h

bool tracking();
void until_line(int speed);

float gyroZ();
void mpu_setup();
void reset_gyroZ();
void gyro_update();

#endif