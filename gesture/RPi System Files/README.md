These are RPi system files that I edited in an attempt to autostart the IMU script when the RPi powers on.

imu_startup.service is located in /etc/systemd/system/ on the RPi. I was unable to get this service working.

.bashrc is located in /home/pi/ on the RPi. I added the last two lines so the IMU script starts immediately after logging into the RPi.
