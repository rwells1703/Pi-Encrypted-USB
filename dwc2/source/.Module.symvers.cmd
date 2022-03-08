cmd_/home/pi/dwc2/Module.symvers := sed 's/ko$$/o/' /home/pi/dwc2/modules.order | scripts/mod/modpost -m -a   -o /home/pi/dwc2/Module.symvers -e -i Module.symvers   -T -
