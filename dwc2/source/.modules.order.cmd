cmd_/home/pi/dwc2/modules.order := {   echo /home/pi/dwc2/dwc2.ko; :; } | awk '!x[$$0]++' - > /home/pi/dwc2/modules.order
