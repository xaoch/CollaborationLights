git clone https://github.com/respeaker/usb_4_mic_array.git
cd usb_4_mic_array
sudo pip3 install pyusb
sudo pip install paho-mqtt
sudo pip install BiblioPixel
sudo pip install rpi_ws281x

/etc/modprobe.d/snd-blacklist.conf 
# add the line, save and reboot
blacklist snd_bcm2835
 
git clone https://github.com/xaoch/CollaborationLights.git
cd CollaborationLights
chmod +x startup.sh
python tuning.py -p