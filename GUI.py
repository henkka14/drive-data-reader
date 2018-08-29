"""Graphical User Interface for the application that is done by kivy graphics library."""

import os
import signal
import socket
import subprocess
from subprocess import Popen
import webbrowser
from pathlib import Path
import datetime as dt
import threading

import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.lang import Builder

import clean_debug_stream as cleaner
import dash_plotter_function as dp


class LoadDialog(Screen):
    clean_data = StringProperty("")

    def load(self, file_selection):
        self.clean_data = os.path.join(
                            os.path.dirname(__file__), 
                            "Cleaned Data",  
                            "clean_data_"\
                             + dt.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
                             )

        _, channels = cleaner.clean_terminal_data_stream(
                                                file_selection[0], 
                                                self.clean_data
                                                )

        dp.initialize_layout(self.clean_data, channels)
        t = threading.Thread(target=dp.app.run_server)
        t.daemon = True
        t.start()
        self.manager.current = "result"

class ResultScreen(Screen):
    ip_adr = socket.gethostbyname(socket.gethostname())
    label_text = StringProperty()
    data_file_text = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_interval(self.check_ip, 1)

    def check_ip(self, dt):
        """This function is used to update ip address on the text link."""

        self.ip_adr = socket.gethostbyname(socket.gethostname())

        self.label_text = (
            'Data has been cleaned! Go to the address '
            '[ref=addr][u]http://127.0.0.1:8050[/u][/ref]'
            ' to view the drive data.\n'
            'Clicking the link opens the browser to view the data. '
            'Data is also saved to\n' + self.data_file_text
        )

    def webopen(self):
        """
        This is used to open web browser when clicking hyperlink.
        See drivedata.kv.
        """

        webbrowser.open_new('http://127.0.0.1:8050')



class DriveDataApp(App):
    """
    Application to process KONE drive data.
    See driverdata.kv for implementation.
    """
        

if __name__ == '__main__':
    #process = MonitoringProcess()
    DriveDataApp().run()