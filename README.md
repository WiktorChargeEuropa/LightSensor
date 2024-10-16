For more energy efficient variant, use crone to start script every time cycle after reboot
So open crontab and add script directory
  sudo crontab -e
  
Use nano, and write line
  @reboot /home/nucadmin/.../LightSensorCycle.sh
  
Remember too add x permission to files, so
  chmod +x LightSensorCycle.sh
  chmod +x LightSensorSingleUse.py
