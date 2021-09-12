
# Copyright 2018, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
"""Skill controlls GPIO on Raspberry Pi.

This allows users to control an LED The LED is Attached to GPIO1

Example:
    literal blocks::

        Turn Led On
        Turn Led Off
        Blink Led
        Led Status

Responses:
    literal blocks::

        Led is Off
        Led is On
        Button Pressed
        Button Released

"""

from os.path import dirname, abspath
import sys
import requests
import json
import threading

sys.path.append(abspath(dirname(__file__)))

from adapt.intent import IntentBuilder
try:
    from mycroft.skills.core import MycroftSkill
except:
    class MycroftSkill:
        pass

#import logging.handlers

import GPIO
""" Includes the GPIO interface"""

__author__ = 'amcgee7'


class GPIO_ControlSkill(MycroftSkill):
    """This is the skill for controlling GPIO of the Raspberry Pi

    Attributes:
        blink_active (bool): Defauts to False and is true while the
            led is suppost to be blinking.  Will be turned to False on
            repeated blink command or when the led is instructed to go
            on or off.
    """

    def on_led_change(self):
        """used to report the state of the led.

        This is attached to the on change event.  And will speak the
        status of the led.
        """
        status = GPIO.get("GPIO1")
        self.speak("Led is %s" % status)
    def on_led2_change(self):
        """used to report the state of the led.

        This is attached to the on change event.  And will speak the
        status of the led.
        """
        status = GPIO.get("GPIO2")
        self.speak("Led is %s" % status)

    def on_button_change(self):
        status = GPIO.get("Button")
        self.speak("Button is %s" % status)

    def __init__(self):
        """This is used to initize the GPIO kill

        This will set the default of blink_active and setup the function
        for listening to the io change.
        """
        self.blink_active = False
        GPIO.on("GPIO1",self.on_led_change)
        GPIO.on("GPIO2",self.on_led2_change)
#        GPIO.on("Button",self.on_button_change)
        super(GPIO_ControlSkill, self).__init__(name="GPIO_ControlSkill")

    def blink_led(self):
        """This Will Start the Led blink process

        This function will start the led blink process and continue
        until blink_active is false.
        """
        if self.blink_active:
            threading.Timer(10, self.blink_led).start()
        if self.blink_active:
            if GPIO.get("GPIO1")!="On":
                GPIO.set("GPIO1","On")
            else:
                GPIO.set("GPIO1","Off")

    def initialize(self):
        """This function will initialize the Skill for Blinking an LED

        This creates two intents
            * IoCommandIntent - Will fire for any command that controlls the LED
            * SystemQueryIntent - Will fire for any system command

        The SystemQueryIntent was desinged for debug info while testing
        and is not required going forward.

        """
        self.load_data_files(dirname(__file__))

        command_intent = IntentBuilder("IoCommandIntent").require("command").require("ioobject").optionally("ioparam").build()
        system_intent = IntentBuilder("SystemQueryIntent").require("question").require("systemobject").build()

        self.register_intent(command_intent, self.handle_command_intent)
        self.register_intent(system_intent, self.handle_system_intent)

    def handle_system_intent(self, message):
        """This is the handeler for system intent.

        This will handle all questions of the system for debug info.

        Args:
            message(obj):
                This is the object containing the message that fired the
                intent.  This is used to discover what to do within the
                intent.
        """
        if message.data["systemobject"] == "Name":
            self.speak_dialog("name")
            self.speak(__name__)
        elif message.data["systemobject"] == "GPIO":
            self.speak_dialog("check")
            if GPIO.is_imported:
                self.speak("GPIO is Imported")
            else:
                self.speak("GPIO is not Imported")
        elif message.data["systemobject"] == "Modules":
            self.speak_dialog("modules")
            for module in sys.modules:
                self.speak(module)
        elif message.data["systemobject"] == "Path":
            self.speak_dialog("path")
            for path in sys.path:
                self.speak(path)

    def handle_command_intent(self, message):
        """This will handle all command intents for controlling GPIO

        This handles all commands to controll the LEDS including checking
        the status.

        Args:
            message(obj):
                This is the object containing the message that fired the
                intent.  This is used to discover what to do within the
                intent.
        """
        if message.data["command"].upper() == "BLINK":
            self.speak_dialog("ledblink")
            if self.blink_active:
                self.blink_active = False
            else:
                self.blink_active = True
                self.blink_led()
        elif message.data["command"].upper() == "STATUS":
            if message.data["ioobject"].upper() == "LED":
                self.on_led_change()
        elif message.data["command"].upper() == "TURN":
            if message.data["ioobject"].upper() == "LED":
                if "ioparam" in message.data:
                    if message.data["ioparam"].upper() == "ON":
                        self.blink_active = False
                        GPIO.set("GPIO1","On")
                    elif message.data["ioparam"].upper() == "OFF":
                        self.blink_active = False
                        GPIO.set("GPIO1","Off")
                else:
                    self.speak_dialog("ipparamrequired")
            if message.data["ioobject"].upper() == "LIGHT":
                if "ioparam" in message.data:
                    if message.data["ioparam"].upper() == "ON":
                        self.blink_active = False
                        GPIO.set("GPIO2","On")
                    elif message.data["ioparam"].upper() == "OFF":
                        self.blink_active = False
                        GPIO.set("GPIO2","Off")
                else:
                    self.speak_dialog("ipparamrequired")
        elif message.data["command"].upper() == "SET":
            if message.data["ioobject"].upper() == "LED":
                if "ioparam" in message.data:
                    if message.data["ioparam"].upper() == "ON":
                        self.blink_active = False
                        GPIO.set("GPIO1","On")
                    elif message.data["ioparam"].upper() == "OFF":
                        self.blink_active = False
                        GPIO.set("GPIO1","Off")
                else:
                    self.speak_dialog("ipparamrequired")
            if message.data["ioobject"].upper() == "LIGHT":
                if "ioparam" in message.data:
                    if message.data["ioparam"].upper() == "ON":
                        self.blink_active = False
                        GPIO.set("GPIO2","On")
                    elif message.data["ioparam"].upper() == "OFF":
                        self.blink_active = False
                        GPIO.set("GPIO2","Off")
                else:
                    self.speak_dialog("ipparamrequired")

    def stop(self):
        """This function will clean up the Skill"""
        self.blink_active = False


def create_skill():
    """This function is to create the skill"""
    return GPIO_ControlSkill()
