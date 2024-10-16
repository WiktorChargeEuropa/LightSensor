For more energyefficient variant, use crone to start script every time cycle after reboot
So
  sudo crontab -e
Use nano, and write line
  @reboot /home/.../.../LightSensorCycle.sh
