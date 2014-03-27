#!/usr/bin/python
import os
import sys
import tty
import json
import time
import subprocess

from datetime import datetime
from evdev import InputDevice, list_devices, ecodes, events

class KeyCash:
    def __init__(self, config_path, scan_device):
        config_file = open(config_path, 'r')
        config_str = config_file.read()
        config_file.close()

        self._config = json.loads(config_str)
        
        self._today_str = datetime.now().strftime('%d-%m-%y')
        self._today_str_old = self._today_str

        if os.path.isfile(self._today_str + '.log'):
            today_file = open(self._today_str + '.log', 'r')
            today_str = today_file.read()
            today_file.close()
            
            self._today_consumed = json.loads(today_str)
        else:
            self._today_consumed = json.loads(config_str)
            
            self.reset_today_consumed()

        self._changes = {}
        
        self._accumulator = []
        
        self._scanner = InputDevice(scan_device)
    
    def reset_changes(self):
        self._changes = {}

    def apply_changes(self):
        for key in self._changes:
            self._today_consumed[key] += self._changes[key]

    def refresh_today(self):
        self._today_str_old = self._today_str
        self._today_str = datetime.now().strftime('%d-%m-%y')
        
        if self._today_str != self._today_str_old:
            self.reset_today_consumed()
    
    def reset_today_consumed(self):
        for key in self._today_consumed:
            self._today_consumed[key] = 0
    
    def write_out_today_consumed(self):
        today_file = open(self._today_str + '.log', 'w+')
        today_file.write(json.dumps(self._today_consumed))
        today_file.close()

    def all_leds_on(self):
        for i in range(10):
            self._keyboard.set_led(i, 1)

    def all_leds_off(self):
        for i in range(10):
            self._keyboard.set_led(i, 0)

    def blink_leds(self):
        self.all_leds_on()
        time.sleep(0.2)
        
        self.all_leds_off()
        time.sleep(0.2)

    def play_sound(self, path):
        subprocess.Popen(['aplay', path])

    def loop(self):
        for event in self._scanner.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = events.KeyEvent(event)
                
                if key_event.keystate == events.KeyEvent.key_down:
                    if key_event.keycode == 'KEY_ENTER':
                        for key in self._config:
                            scanner_code = ''.join([ elem[-1:] for elem in self._accumulator])
                            
                            if scanner_code == self._config[key]['scanner_code']:
                                self.refresh_today()
                                
                                self.play_sound(self._config[key]['sound_file'])
                                
                                if not key in self._changes:
                                    self._changes[key] = 1
                                else:
                                    self._changes[key] += 1
                                
                                self.apply_changes()
                                self.reset_changes()
                                
                                self.write_out_today_consumed()
                        
                        self._accumulator = []
                    else:
                        self._accumulator.append(key_event.keycode)

if __name__ == '__main__':
    key_cash = KeyCash('cash.conf', '/dev/input/event0')
    
    key_cash.loop()
