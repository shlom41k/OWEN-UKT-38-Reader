# -*- coding: utf-8 -*-
import sys
import numpy as np
import serial.tools.list_ports
import serial
import pygame
from datetime import datetime, date, time
from matplotlib import *
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import style
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1.mpl_axes import Axes

from PyQt5 import QtGui
#from PyQt5 import QtWidgets
import ResursSoft
import ChannelsDescription
import OWENReader
import TmpToFile

from threading import Thread
from time import sleep
#from OWEN.scripts.ResursSoft import QtCore, QtGui, QtWidgets


class UIMainApp(ResursSoft.QtWidgets.QMainWindow, ResursSoft.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.DateTimeThread = Thread(target=self.UpdateDateTime, daemon=True)
        self.DateTimeThread.start()

        self.LoadChNames()
        self.SearchCOMPorts()

        self.btn_disconnect.setDisabled(True)
        self.read_EN = True

        self.NumOfTMPPlotPts = 0
        self.NumOfTMPPts = 0

        self.TrackSleepTime = 2
        self.PlayMusicEN = False

        self.RowCnt = 0

        self.tmp_ch_1 = []
        self.tmp_ch_2 = []
        self.tmp_ch_3 = []
        self.tmp_ch_4 = []
        self.tmp_ch_5 = []
        self.tmp_ch_6 = []
        self.tmp_ch_7 = []
        self.tmp_ch_8 = []
        self.DateTime = []

        self.btn_load_desc_ch.clicked.connect(self.LoadChNames)
        self.btn_save_desc_ch.clicked.connect(self.SaveChNames)

        self.ch_com_port.currentTextChanged.connect(self.ChooseCOMPorts)
        self.btn_connect.clicked.connect(self.ConnectToCOM)
        self.btn_disconnect.clicked.connect(self.DisconnectCOM)

        self.bth_create_logfile.clicked.connect(self.ChooseLogFile)
        self.ch_save_to_file.stateChanged.connect(self.LogToFileCheck)

        self.ch_sound.stateChanged.connect(self.SirenCheck)

        self.ch_tmp_en_ch_1.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_2.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_3.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_4.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_5.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_6.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_7.stateChanged.connect(self.EnabledAxes)
        self.ch_tmp_en_ch_8.stateChanged.connect(self.EnabledAxes)

        self.ch_tmp_ch_1.clicked.connect(self.Ch1TrackCheck)
        self.ch_tmp_ch_2.clicked.connect(self.Ch2TrackCheck)
        self.ch_tmp_ch_3.clicked.connect(self.Ch3TrackCheck)
        self.ch_tmp_ch_4.clicked.connect(self.Ch4TrackCheck)
        self.ch_tmp_ch_5.clicked.connect(self.Ch5TrackCheck)
        self.ch_tmp_ch_6.clicked.connect(self.Ch6TrackCheck)
        self.ch_tmp_ch_7.clicked.connect(self.Ch7TrackCheck)
        self.ch_tmp_ch_8.clicked.connect(self.Ch8TrackCheck)

        self.btn_tmp_pts_1.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_2.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_3.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_4.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_5.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_6.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_7.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_8.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_9.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_10.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_11.clicked.connect(self.ChooseTMPPlotPts)
        self.btn_tmp_pts_12.clicked.connect(self.ChooseTMPPlotPts)

        self.btn_tmp_pts_12.setChecked(True)


# Work with channelnames
    def SaveChNames(self):
        self.ChannelNames = {
            'Channel 1': str(self.lbl_ed_name_ch_1.text()),
            'Channel 2': str(self.lbl_ed_name_ch_2.text()),
            'Channel 3': str(self.lbl_ed_name_ch_3.text()),
            'Channel 4': str(self.lbl_ed_name_ch_4.text()),
            'Channel 5': str(self.lbl_ed_name_ch_5.text()),
            'Channel 6': str(self.lbl_ed_name_ch_6.text()),
            'Channel 7': str(self.lbl_ed_name_ch_7.text()),
            'Channel 8': str(self.lbl_ed_name_ch_8.text())
        }
        ChannelsDescription.SaveChannelNames(self.ChannelNames)
        print("Channels description save to file")
    def LoadChNames(self):
        try:
            self.ChannelNames = ChannelsDescription.LoadChannelNames()
            self.lbl_ed_name_ch_1.setText(self.ChannelNames.get("Channel 1"))
            self.lbl_ed_name_ch_2.setText(self.ChannelNames.get("Channel 2"))
            self.lbl_ed_name_ch_3.setText(self.ChannelNames.get("Channel 3"))
            self.lbl_ed_name_ch_4.setText(self.ChannelNames.get("Channel 4"))
            self.lbl_ed_name_ch_5.setText(self.ChannelNames.get("Channel 5"))
            self.lbl_ed_name_ch_6.setText(self.ChannelNames.get("Channel 6"))
            self.lbl_ed_name_ch_7.setText(self.ChannelNames.get("Channel 7"))
            self.lbl_ed_name_ch_8.setText(self.ChannelNames.get("Channel 8"))
            print("Channels description load from file")
        except:
            TmpToFile.WriteErrorToLog("Error to load and set channel names")
            print("Error to load and set channel names")


#Work witn COM port
    def SearchCOMPorts(self):
        self.ports = OWENReader.SearchCOMPorts()
        print(self.ports)
        self.ch_com_port.clear()
        try:
            for port in self.ports:
                self.ch_com_port.addItem(port)
            self.lbl_portname.setText(self.ports.get(self.ch_com_port.currentText()))
            self.lbl_portname.setStyleSheet("color: blue")
        except:
            print("COM-ports are not detected :(")
            TmpToFile.WriteErrorToLog("COM-ports are not detected :(")
            self.lbl_portname.setText("No available COM ports :(")
            self.lbl_portname.setStyleSheet("color: red")

        if self.ch_com_port.currentIndex() == -1:
            self.lbl_portname.setText("No available COM ports :(")
            self.lbl_portname.setStyleSheet("color: red")
            self.btn_connect.setDisabled(True)
        else:
            self.btn_connect.setEnabled(True)
    def ChooseCOMPorts(self):
        if self.ch_com_port.currentIndex() == -1:
            self.lbl_portname.setText("No available COM ports :(")
            self.lbl_portname.setStyleSheet("color: red")

        else:
            self.lbl_portname.setText(self.ports.get(self.ch_com_port.currentText()))
            self.lbl_portname.setStyleSheet("color: blue")
    def ConnectToCOM(self):
        try:
            self.ser = OWENReader.CreateSerialPort(self.ch_com_port.currentText())

            if ~(self.ser.isOpen()):
                self.ser.open()

            self.btn_disconnect.setEnabled(True)
            self.btn_connect.setDisabled(True)
            self.ch_com_port.setDisabled(True)
            self.lbl_portname.setStyleSheet("color: green")
            self.lbl_totalpts_txt.setEnabled(True)
            self.lbl_tmp_totalpts.setEnabled(True)
        except:
            TmpToFile.WriteErrorToLog("Error with connection to serial port")
            print("Error with connection to serial port")
            self.lbl_portname.setStyleSheet("color: red")

        if self.ser.isOpen():
            self.read_EN = True
            self.TMPReadThread = Thread(target=self.StartTMPRead)
            self.TMPReadThread.start()

            self.TMPUpdateThread = Thread(target=self.StartUpdate)
            self.TMPUpdateThread.start()
        else:
            #print("Serial port is not opened")
            try:
                self.ser.close()
            except:
                pass

    def StartTMPRead(self):
        while self.read_EN:
            try:
                self.lbl_portname.setStyleSheet("color: green")
                OWENReader.ConnectToAC2(self.ser)
                BROADCAST_FLAG = OWENReader.IsReadyToWork(self.ser)

                if BROADCAST_FLAG:
                    TMP, READ_CORRECT_FLAG = OWENReader.Read16Bytes(self.ser)

                    if READ_CORRECT_FLAG:
                        tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5, tmp_ch_6, tmp_ch_7, tmp_ch_8 = OWENReader.GetTMPValues(
                            TMP)
                        Valid_Flag = OWENReader.IsValuesValid(tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5, tmp_ch_6, tmp_ch_7, tmp_ch_8)
                        if Valid_Flag:
                            self.NumOfTMPPts = self.NumOfTMPPts + 1
                            self.DateTime.append(datetime.now())
                            self.tmp_ch_1.append(tmp_ch_1)
                            self.tmp_ch_2.append(tmp_ch_2)
                            self.tmp_ch_3.append(tmp_ch_3)
                            self.tmp_ch_4.append(tmp_ch_4)
                            self.tmp_ch_5.append(tmp_ch_5)
                            self.tmp_ch_6.append(tmp_ch_6)
                            self.tmp_ch_7.append(tmp_ch_7)
                            self.tmp_ch_8.append(tmp_ch_8)
                            if self.ch_save_to_file.isChecked():
                                try:
                                    TmpToFile.DataToFile(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5,
                                                         tmp_ch_6, tmp_ch_7, tmp_ch_8, self.LogPath, sep=", ")
                                except:
                                    TmpToFile.WriteErrorToLog("Error when try write data to file")
                                    print("Error when try write data to file")
                            try:
                                self.UpdateTable()
                            except:
                                TmpToFile.WriteErrorToLog("Error when try to write data in table")
                                print("Error when try to write data in table")
                        print(tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5, tmp_ch_6, tmp_ch_7, tmp_ch_8)
                else:
                    #self.ser.close()
                    TmpToFile.WriteErrorToLog("No response from OWEN (wait 0x55h)")
                    print("No response from OWEN (wait 0x55h)")
                    self.lbl_portname.setStyleSheet("color: red")

            except:
                TmpToFile.WriteErrorToLog("Error communicating")
                print("Error communicating")
                #self.ser.close()
            sleep(5)

        if self.ser.isOpen():
            self.ser.close()

    def DisconnectCOM(self):
        self.read_EN = False
        sleep(0.1)
        self.lbl_portname.setStyleSheet("color: blue")
        self.lbl_totalpts_txt.setDisabled(True)
        self.lbl_tmp_totalpts.setDisabled(True)
        self.CloseTrackLabels()
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setDisabled(True)
        self.ch_com_port.setEnabled(True)
        try:
            if self.ser.isOpen():
                self.ser.close()
            print("Serial port " + str(self.ser.name) + " is closed")
        except:
            print("No active ports")


# Work with GUI
    def OpenTrackLabesl(self):
        self.ed_tmp_min_ch_1.setEnabled(True)
        self.ed_tmp_max_ch_1.setEnabled(True)
        self.ch_tmp_ch_1.setEnabled(True)
        self.ed_tmp_min_ch_2.setEnabled(True)
        self.ed_tmp_max_ch_2.setEnabled(True)
        self.ch_tmp_ch_2.setEnabled(True)
        self.ed_tmp_min_ch_3.setEnabled(True)
        self.ed_tmp_max_ch_3.setEnabled(True)
        self.ch_tmp_ch_3.setEnabled(True)
        self.ed_tmp_min_ch_4.setEnabled(True)
        self.ed_tmp_max_ch_4.setEnabled(True)
        self.ch_tmp_ch_4.setEnabled(True)
        self.ed_tmp_min_ch_5.setEnabled(True)
        self.ed_tmp_max_ch_5.setEnabled(True)
        self.ch_tmp_ch_5.setEnabled(True)
        self.ed_tmp_min_ch_6.setEnabled(True)
        self.ed_tmp_max_ch_6.setEnabled(True)
        self.ch_tmp_ch_6.setEnabled(True)
        self.ed_tmp_min_ch_7.setEnabled(True)
        self.ed_tmp_max_ch_7.setEnabled(True)
        self.ch_tmp_ch_7.setEnabled(True)
        self.ed_tmp_min_ch_8.setEnabled(True)
        self.ed_tmp_max_ch_8.setEnabled(True)
        self.ch_tmp_ch_8.setEnabled(True)

        self.ch_sound.setEnabled(True)
    def CloseTrackLabels(self):
        self.StopCheking()
        self.ed_tmp_min_ch_1.setDisabled(True)
        self.ed_tmp_max_ch_1.setDisabled(True)
        self.ed_tmp_min_ch_1.setStyleSheet("background: white")
        self.ed_tmp_max_ch_1.setStyleSheet("background: white")
        self.ch_tmp_ch_1.setChecked(False)
        self.ch_tmp_ch_1.setDisabled(True)
        self.ed_tmp_min_ch_2.setDisabled(True)
        self.ed_tmp_max_ch_2.setDisabled(True)
        self.ed_tmp_min_ch_2.setStyleSheet("background: white")
        self.ed_tmp_max_ch_2.setStyleSheet("background: white")
        self.ch_tmp_ch_2.setChecked(False)
        self.ch_tmp_ch_2.setDisabled(True)
        self.ed_tmp_min_ch_3.setDisabled(True)
        self.ed_tmp_max_ch_3.setDisabled(True)
        self.ed_tmp_min_ch_3.setStyleSheet("background: white")
        self.ed_tmp_max_ch_3.setStyleSheet("background: white")
        self.ch_tmp_ch_3.setChecked(False)
        self.ch_tmp_ch_3.setDisabled(True)
        self.ed_tmp_min_ch_4.setDisabled(True)
        self.ed_tmp_max_ch_4.setDisabled(True)
        self.ed_tmp_min_ch_4.setStyleSheet("background: white")
        self.ed_tmp_max_ch_4.setStyleSheet("background: white")
        self.ch_tmp_ch_4.setChecked(False)
        self.ch_tmp_ch_4.setDisabled(True)
        self.ed_tmp_min_ch_5.setDisabled(True)
        self.ed_tmp_max_ch_5.setDisabled(True)
        self.ed_tmp_min_ch_5.setStyleSheet("background: white")
        self.ed_tmp_max_ch_5.setStyleSheet("background: white")
        self.ch_tmp_ch_5.setChecked(False)
        self.ch_tmp_ch_5.setDisabled(True)
        self.ed_tmp_min_ch_6.setDisabled(True)
        self.ed_tmp_max_ch_6.setDisabled(True)
        self.ed_tmp_min_ch_6.setStyleSheet("background: white")
        self.ed_tmp_max_ch_6.setStyleSheet("background: white")
        self.ch_tmp_ch_6.setChecked(False)
        self.ch_tmp_ch_6.setDisabled(True)
        self.ed_tmp_min_ch_7.setDisabled(True)
        self.ed_tmp_max_ch_7.setDisabled(True)
        self.ed_tmp_min_ch_7.setStyleSheet("background: white")
        self.ed_tmp_max_ch_7.setStyleSheet("background: white")
        self.ch_tmp_ch_7.setChecked(False)
        self.ch_tmp_ch_7.setDisabled(True)
        self.ed_tmp_min_ch_8.setDisabled(True)
        self.ed_tmp_max_ch_8.setDisabled(True)
        self.ed_tmp_min_ch_8.setStyleSheet("background: white")
        self.ed_tmp_max_ch_8.setStyleSheet("background: white")
        self.ch_tmp_ch_8.setChecked(False)
        self.ch_tmp_ch_8.setDisabled(True)

        self.ch_sound.setDisabled(True)
        self.ch_sound.setChecked(False)
    def StopCheking(self):
        self.tmp_track_ch1_EN = False
        self.tmp_track_ch2_EN = False
        self.tmp_track_ch3_EN = False
        self.tmp_track_ch4_EN = False
        self.tmp_track_ch5_EN = False
        self.tmp_track_ch6_EN = False
        self.tmp_track_ch7_EN = False
        self.tmp_track_ch8_EN = False
    def EnabledAxes(self):
        if not (self.ch_tmp_en_ch_1.isChecked()):
            self.ax_tmp_ch_1.cla()
            self.ax_tmp_ch_1.clear()
            plt.setp(self.ax_tmp_ch_1.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_1.get_yticklabels(), visible=False)
            self.tmp_ch_1_Figure.canvas.draw()

            self.lbl_act_tmp_ch_1.setText(str(0.0))
            self.lbl_act_tmp_ch_1.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_1.setEnabled(True)

        if not (self.ch_tmp_en_ch_2.isChecked()):
            self.ax_tmp_ch_2.cla()
            self.ax_tmp_ch_2.clear()
            plt.setp(self.ax_tmp_ch_2.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_2.get_yticklabels(), visible=False)
            self.tmp_ch_2_Figure.canvas.draw()

            self.lbl_act_tmp_ch_2.setText(str(0.0))
            self.lbl_act_tmp_ch_2.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_2.setEnabled(True)

        if not (self.ch_tmp_en_ch_3.isChecked()):
            self.ax_tmp_ch_3.cla()
            self.ax_tmp_ch_3.clear()
            plt.setp(self.ax_tmp_ch_3.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_3.get_yticklabels(), visible=False)
            self.tmp_ch_3_Figure.canvas.draw()

            self.lbl_act_tmp_ch_3.setText(str(0.0))
            self.lbl_act_tmp_ch_3.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_3.setEnabled(True)

        if not (self.ch_tmp_en_ch_4.isChecked()):
            self.ax_tmp_ch_4.cla()
            self.ax_tmp_ch_4.clear()
            plt.setp(self.ax_tmp_ch_4.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_4.get_yticklabels(), visible=False)
            self.tmp_ch_4_Figure.canvas.draw()

            self.lbl_act_tmp_ch_4.setText(str(0.0))
            self.lbl_act_tmp_ch_4.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_4.setEnabled(True)

        if not (self.ch_tmp_en_ch_5.isChecked()):
            self.ax_tmp_ch_5.cla()
            self.ax_tmp_ch_5.clear()
            plt.setp(self.ax_tmp_ch_5.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_5.get_yticklabels(), visible=False)
            self.tmp_ch_5_Figure.canvas.draw()

            self.lbl_act_tmp_ch_5.setText(str(0.0))
            self.lbl_act_tmp_ch_5.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_5.setEnabled(True)

        if not (self.ch_tmp_en_ch_6.isChecked()):
            self.ax_tmp_ch_6.cla()
            self.ax_tmp_ch_6.clear()
            plt.setp(self.ax_tmp_ch_6.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_6.get_yticklabels(), visible=False)
            self.tmp_ch_6_Figure.canvas.draw()

            self.lbl_act_tmp_ch_6.setText(str(0.0))
            self.lbl_act_tmp_ch_6.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_6.setEnabled(True)

        if not (self.ch_tmp_en_ch_7.isChecked()):
            self.ax_tmp_ch_7.cla()
            self.ax_tmp_ch_7.clear()
            plt.setp(self.ax_tmp_ch_7.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_7.get_yticklabels(), visible=False)
            self.tmp_ch_7_Figure.canvas.draw()

            self.lbl_act_tmp_ch_7.setText(str(0.0))
            self.lbl_act_tmp_ch_7.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_7.setEnabled(True)

        if not (self.ch_tmp_en_ch_8.isChecked()):
            self.ax_tmp_ch_8.cla()
            self.ax_tmp_ch_8.clear()
            plt.setp(self.ax_tmp_ch_8.get_xticklabels(), visible=False)
            plt.setp(self.ax_tmp_ch_8.get_yticklabels(), visible=False)
            self.tmp_ch_8_Figure.canvas.draw()

            self.lbl_act_tmp_ch_8.setText(str(0.0))
            self.lbl_act_tmp_ch_8.setDisabled(True)
        else:
            self.lbl_act_tmp_ch_8.setEnabled(True)
    def OpenTMPButtons(self):
        if self.NumOfTMPPts > 20000:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setEnabled(True)
            self.btn_tmp_pts_10.setEnabled(True)
            self.btn_tmp_pts_9.setEnabled(True)
            self.btn_tmp_pts_8.setEnabled(True)
            self.btn_tmp_pts_7.setEnabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 10000:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setEnabled(True)
            self.btn_tmp_pts_9.setEnabled(True)
            self.btn_tmp_pts_8.setEnabled(True)
            self.btn_tmp_pts_7.setEnabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 5000:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setEnabled(True)
            self.btn_tmp_pts_8.setEnabled(True)
            self.btn_tmp_pts_7.setEnabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 2000:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setEnabled(True)
            self.btn_tmp_pts_7.setEnabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 1000:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setEnabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 500:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setEnabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 200:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setEnabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 100:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setDisabled(True)
            self.btn_tmp_pts_4.setEnabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 50:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setDisabled(True)
            self.btn_tmp_pts_4.setDisabled(True)
            self.btn_tmp_pts_3.setEnabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 20:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setDisabled(True)
            self.btn_tmp_pts_4.setDisabled(True)
            self.btn_tmp_pts_3.setDisabled(True)
            self.btn_tmp_pts_2.setEnabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        elif self.NumOfTMPPts > 10:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setDisabled(True)
            self.btn_tmp_pts_4.setDisabled(True)
            self.btn_tmp_pts_3.setDisabled(True)
            self.btn_tmp_pts_2.setDisabled(True)
            self.btn_tmp_pts_1.setEnabled(True)
        else:
            self.btn_tmp_pts_12.setEnabled(True)
            self.btn_tmp_pts_11.setDisabled(True)
            self.btn_tmp_pts_10.setDisabled(True)
            self.btn_tmp_pts_9.setDisabled(True)
            self.btn_tmp_pts_8.setDisabled(True)
            self.btn_tmp_pts_7.setDisabled(True)
            self.btn_tmp_pts_6.setDisabled(True)
            self.btn_tmp_pts_5.setDisabled(True)
            self.btn_tmp_pts_4.setDisabled(True)
            self.btn_tmp_pts_3.setDisabled(True)
            self.btn_tmp_pts_2.setDisabled(True)
            self.btn_tmp_pts_1.setDisabled(True)
    def ChooseTMPPlotPts(self):
        if self.btn_tmp_pts_1.isChecked():
            self.NumOfTMPPlotPts = 10
        elif self.btn_tmp_pts_2.isChecked():
            self.NumOfTMPPlotPts = 20
        elif self.btn_tmp_pts_3.isChecked():
            self.NumOfTMPPlotPts = 50
        elif self.btn_tmp_pts_4.isChecked():
            self.NumOfTMPPlotPts = 100
        elif self.btn_tmp_pts_5.isChecked():
            self.NumOfTMPPlotPts = 200
        elif self.btn_tmp_pts_6.isChecked():
            self.NumOfTMPPlotPts = 500
        elif self.btn_tmp_pts_7.isChecked():
            self.NumOfTMPPlotPts = 1000
        elif self.btn_tmp_pts_8.isChecked():
            self.NumOfTMPPlotPts = 2000
        elif self.btn_tmp_pts_9.isChecked():
            self.NumOfTMPPlotPts = 5000
        elif self.btn_tmp_pts_10.isChecked():
            self.NumOfTMPPlotPts = 10000
        elif self.btn_tmp_pts_11.isChecked():
            self.NumOfTMPPlotPts = 20000
        else:
            self.NumOfTMPPlotPts = 0

# Work with check TMP pannel
    def Ch1TrackCheck(self):
        if self.ch_tmp_ch_1.isChecked():
            self.ed_tmp_min_ch_1.setDisabled(True)
            self.ed_tmp_max_ch_1.setDisabled(True)
            self.tmp_track_ch1_EN = True
            self.Ch1TrackThread = Thread(target=self.Ch1Track)
            self.Ch1TrackThread.start()
        else:
            self.ed_tmp_min_ch_1.setEnabled(True)
            self.ed_tmp_max_ch_1.setEnabled(True)
            self.ed_tmp_min_ch_1.setStyleSheet("background: white")
            self.ed_tmp_max_ch_1.setStyleSheet("background: white")
            self.tmp_track_ch1_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch2TrackCheck(self):
        if self.ch_tmp_ch_2.isChecked():
            self.ed_tmp_min_ch_2.setDisabled(True)
            self.ed_tmp_max_ch_2.setDisabled(True)
            self.tmp_track_ch2_EN = True
            self.Ch2TrackThread = Thread(target=self.Ch2Track)
            self.Ch2TrackThread.start()
        else:
            self.ed_tmp_min_ch_2.setEnabled(True)
            self.ed_tmp_max_ch_2.setEnabled(True)
            self.ed_tmp_min_ch_2.setStyleSheet("background: white")
            self.ed_tmp_max_ch_2.setStyleSheet("background: white")
            self.tmp_track_ch2_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch3TrackCheck(self):
        if self.ch_tmp_ch_3.isChecked():
            self.ed_tmp_min_ch_3.setDisabled(True)
            self.ed_tmp_max_ch_3.setDisabled(True)
            self.tmp_track_ch3_EN = True
            self.Ch3TrackThread = Thread(target=self.Ch3Track)
            self.Ch3TrackThread.start()
        else:
            self.ed_tmp_min_ch_3.setEnabled(True)
            self.ed_tmp_max_ch_3.setEnabled(True)
            self.ed_tmp_min_ch_3.setStyleSheet("background: white")
            self.ed_tmp_max_ch_3.setStyleSheet("background: white")
            self.tmp_track_ch3_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch4TrackCheck(self):
        if self.ch_tmp_ch_4.isChecked():
            self.ed_tmp_min_ch_4.setDisabled(True)
            self.ed_tmp_max_ch_4.setDisabled(True)
            self.tmp_track_ch4_EN = True
            self.Ch4TrackThread = Thread(target=self.Ch4Track)
            self.Ch4TrackThread.start()
        else:
            self.ed_tmp_min_ch_4.setEnabled(True)
            self.ed_tmp_max_ch_4.setEnabled(True)
            self.ed_tmp_min_ch_4.setStyleSheet("background: white")
            self.ed_tmp_max_ch_4.setStyleSheet("background: white")
            self.tmp_track_ch4_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch5TrackCheck(self):
        if self.ch_tmp_ch_5.isChecked():
            self.ed_tmp_min_ch_5.setDisabled(True)
            self.ed_tmp_max_ch_5.setDisabled(True)
            self.tmp_track_ch5_EN = True
            self.Ch5TrackThread = Thread(target=self.Ch5Track)
            self.Ch5TrackThread.start()
        else:
            self.ed_tmp_min_ch_5.setEnabled(True)
            self.ed_tmp_max_ch_5.setEnabled(True)
            self.ed_tmp_min_ch_5.setStyleSheet("background: white")
            self.ed_tmp_max_ch_5.setStyleSheet("background: white")
            self.tmp_track_ch5_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch6TrackCheck(self):
        if self.ch_tmp_ch_6.isChecked():
            self.ed_tmp_min_ch_6.setDisabled(True)
            self.ed_tmp_max_ch_6.setDisabled(True)
            self.tmp_track_ch6_EN = True
            self.Ch6TrackThread = Thread(target=self.Ch6Track)
            self.Ch6TrackThread.start()
        else:
            self.ed_tmp_min_ch_6.setEnabled(True)
            self.ed_tmp_max_ch_6.setEnabled(True)
            self.ed_tmp_min_ch_6.setStyleSheet("background: white")
            self.ed_tmp_max_ch_6.setStyleSheet("background: white")
            self.tmp_track_ch6_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch7TrackCheck(self):
        if self.ch_tmp_ch_7.isChecked():
            self.ed_tmp_min_ch_7.setDisabled(True)
            self.ed_tmp_max_ch_7.setDisabled(True)
            self.tmp_track_ch7_EN = True
            self.Ch7TrackThread = Thread(target=self.Ch7Track)
            self.Ch7TrackThread.start()
        else:
            self.ed_tmp_min_ch_7.setEnabled(True)
            self.ed_tmp_max_ch_7.setEnabled(True)
            self.ed_tmp_min_ch_7.setStyleSheet("background: white")
            self.ed_tmp_max_ch_7.setStyleSheet("background: white")
            self.tmp_track_ch7_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")
    def Ch8TrackCheck(self):
        if self.ch_tmp_ch_8.isChecked():
            self.ed_tmp_min_ch_8.setDisabled(True)
            self.ed_tmp_max_ch_8.setDisabled(True)
            self.tmp_track_ch8_EN = True
            self.Ch8TrackThread = Thread(target=self.Ch8Track)
            self.Ch8TrackThread.start()
        else:
            self.ed_tmp_min_ch_8.setEnabled(True)
            self.ed_tmp_max_ch_8.setEnabled(True)
            self.ed_tmp_min_ch_8.setStyleSheet("background: white")
            self.ed_tmp_max_ch_8.setStyleSheet("background: white")
            self.tmp_track_ch8_EN = False
            try:
                pygame.mixer.music.stop()
                self.PlayMusicEN = False
            except:
                print("No playing sounds")

    def Ch1Track(self):
        while self.tmp_track_ch1_EN:
            try:
                if float(self.ed_tmp_min_ch_1.text()) <= self.tmp_ch_1[-1] <= float(self.ed_tmp_max_ch_1.text()):
                    self.ed_tmp_min_ch_1.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_1.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_1.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_1.setStyleSheet("background: #fc6868")
                    if self.ch_sound.isChecked():
                        if not (self.PlayMusicEN):
                            self.StartAlarmThread()
                            sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 1 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch2Track(self):
        while self.tmp_track_ch2_EN:
            try:
                if float(self.ed_tmp_min_ch_2.text()) <= self.tmp_ch_2[-1] <= float(self.ed_tmp_max_ch_2.text()):
                    self.ed_tmp_min_ch_2.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_2.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_2.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_2.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 2 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch3Track(self):
        while self.tmp_track_ch3_EN:
            try:
                if float(self.ed_tmp_min_ch_3.text()) <= self.tmp_ch_3[-1] <= float(self.ed_tmp_max_ch_3.text()):
                    self.ed_tmp_min_ch_3.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_3.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_3.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_3.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 3 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch4Track(self):
        while self.tmp_track_ch4_EN:
            try:
                if float(self.ed_tmp_min_ch_4.text()) <= self.tmp_ch_4[-1] <= float(self.ed_tmp_max_ch_4.text()):
                    self.ed_tmp_min_ch_4.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_4.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_4.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_4.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 4 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch5Track(self):
        while self.tmp_track_ch5_EN:
            try:
                if float(self.ed_tmp_min_ch_5.text()) <= self.tmp_ch_5[-1] <= float(self.ed_tmp_max_ch_5.text()):
                    self.ed_tmp_min_ch_5.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_5.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_5.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_5.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 5 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch6Track(self):
        while self.tmp_track_ch6_EN:
            try:
                if float(self.ed_tmp_min_ch_6.text()) <= self.tmp_ch_6[-1] <= float(self.ed_tmp_max_ch_6.text()):
                    self.ed_tmp_min_ch_6.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_6.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_6.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_6.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 6 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch7Track(self):
        while self.tmp_track_ch7_EN:
            try:
                if float(self.ed_tmp_min_ch_7.text()) <= self.tmp_ch_7[-1] <= float(self.ed_tmp_max_ch_7.text()):
                    self.ed_tmp_min_ch_7.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_7.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_7.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_7.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 7 tracking not worked")
            sleep(self.TrackSleepTime)
    def Ch8Track(self):
        while self.tmp_track_ch8_EN:
            try:
                if float(self.ed_tmp_min_ch_8.text()) <= self.tmp_ch_8[-1] <= float(self.ed_tmp_max_ch_8.text()):
                    self.ed_tmp_min_ch_8.setStyleSheet("background: #96fac0")
                    self.ed_tmp_max_ch_8.setStyleSheet("background: #96fac0")
                else:
                    self.ed_tmp_min_ch_8.setStyleSheet("background: #fc6868")
                    self.ed_tmp_max_ch_8.setStyleSheet("background: #fc6868")
                    if not (self.PlayMusicEN):
                        self.StartAlarmThread()
                        sleep(10)
            except ValueError:
                print("Please, use '.' as delimiter (example: 0.5)")
            except:
                print("Channel 8 tracking not worked")
            sleep(self.TrackSleepTime)



# Update figures and labels
    def StartUpdate(self):
        self.OpenTrackLabesl()
        self.gb_tmp_pts.setEnabled(True)
        self.OpenTMPButtons()
        while self.read_EN:
            if len(self.tmp_ch_1) > 0:
                self.Update_TMP_lbl()
                self.Update_TMP_Track_lbl()

            if len(self.tmp_ch_1) > 1:
                self.Update_TMP_figures()

            self.lbl_tmp_totalpts.setText(str(self.NumOfTMPPts))
            self.OpenTMPButtons()
            sleep(5)
    def Update_TMP_figures(self):
        #-- Update figure tmp_ch_1 --
        if self.ch_tmp_en_ch_1.isChecked():
            self.ax_tmp_ch_1.clear()
            self.tmp_ch1_line, = self.ax_tmp_ch_1.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_1[-self.NumOfTMPPlotPts:],
                                                       color='b', linestyle='solid', label='TMP_TP_1', linewidth=1)
            self.ax_tmp_ch_1.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_1.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_1.set_facecolor('w')
            self.ax_tmp_ch_1.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                   max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_1.set_ylim(min(self.tmp_ch_1[-self.NumOfTMPPlotPts:]) - 0.01,
                                   max(self.tmp_ch_1[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_1.yaxis.label.set_color('blue')
            self.ax_tmp_ch_1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            self.myXLabel = mdates.DateFormatter("%H:%M:%S")
            self.ax_tmp_ch_1.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_1.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_1.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_1_Figure.canvas.draw()
            self.tmp_ch_1_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_2 --
        if self.ch_tmp_en_ch_2.isChecked():
            self.ax_tmp_ch_2.clear()
            self.tmp_ch2_line, = self.ax_tmp_ch_2.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_2[-self.NumOfTMPPlotPts:],
                                                       color='#4fffff', linestyle='solid', label='TMP_TP_2', linewidth=1)
            self.ax_tmp_ch_2.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_2.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_2.set_facecolor('w')
            self.ax_tmp_ch_2.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_2.set_ylim(min(self.tmp_ch_2[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_2[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_2.yaxis.label.set_color('blue')
            #self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            #self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_2.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_2.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_2.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_2_Figure.canvas.draw()
            self.tmp_ch_2_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_3 --
        if self.ch_tmp_en_ch_3.isChecked():
            self.ax_tmp_ch_3.clear()
            self.tmp_ch3_line, = self.ax_tmp_ch_3.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_3[-self.NumOfTMPPlotPts:],
                                                       color='r', linestyle='solid', label='TMP_TP_3', linewidth=1)
            self.ax_tmp_ch_3.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_3.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_3.set_facecolor('w')
            self.ax_tmp_ch_3.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_3.set_ylim(min(self.tmp_ch_3[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_3[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_3.yaxis.label.set_color('blue')
            # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            # self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_3.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_3.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_3.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_3_Figure.canvas.draw()
            self.tmp_ch_3_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_4 --
        if self.ch_tmp_en_ch_4.isChecked():
            self.ax_tmp_ch_4.clear()
            self.tmp_ch4_line, = self.ax_tmp_ch_4.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_4[-self.NumOfTMPPlotPts:],
                                                       color='#ff00fb', linestyle='solid', label='TMP_TP_4', linewidth=1)
            self.ax_tmp_ch_4.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_4.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_4.set_facecolor('w')
            self.ax_tmp_ch_4.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_4.set_ylim(min(self.tmp_ch_4[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_4[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_4.yaxis.label.set_color('blue')
            # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            # self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_4.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_4.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_4.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_4_Figure.canvas.draw()
            self.tmp_ch_4_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_5 --
        if self.ch_tmp_en_ch_5.isChecked():
            self.ax_tmp_ch_5.clear()
            self.tmp_ch5_line, = self.ax_tmp_ch_5.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_5[-self.NumOfTMPPlotPts:],
                                                       color='#00FF00', linestyle='solid', label='TMP_TP_5', linewidth=1)
            self.ax_tmp_ch_5.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_5.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_5.set_facecolor('w')
            self.ax_tmp_ch_5.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_5.set_ylim(min(self.tmp_ch_5[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_5[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_5.yaxis.label.set_color('blue')
            # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            # self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_5.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_5.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_5.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_5_Figure.canvas.draw()
            self.tmp_ch_5_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_6 --
        if self.ch_tmp_en_ch_6.isChecked():
            self.ax_tmp_ch_6.clear()
            self.tmp_ch6_line, = self.ax_tmp_ch_6.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_6[-self.NumOfTMPPlotPts:],
                                                       color='#f5d311', linestyle='solid', label='TMP_TP_6', linewidth=1)
            self.ax_tmp_ch_6.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_6.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_6.set_facecolor('w')
            self.ax_tmp_ch_6.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_6.set_ylim(min(self.tmp_ch_6[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_6[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_6.yaxis.label.set_color('blue')
            # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            # self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_6.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_6.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_6.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_6_Figure.canvas.draw()
            self.tmp_ch_6_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_7 --
        if self.ch_tmp_en_ch_7.isChecked():
            self.ax_tmp_ch_7.clear()
            self.tmp_ch7_line, = self.ax_tmp_ch_7.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_7[-self.NumOfTMPPlotPts:],
                                                       color='#b700ff', linestyle='solid', label='TMP_TP_6', linewidth=1)
            self.ax_tmp_ch_7.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
            self.ax_tmp_ch_7.grid(c='k', ls='--', lw=0.1)
            self.ax_tmp_ch_7.set_facecolor('w')
            self.ax_tmp_ch_7.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                      max(self.DateTime[-self.NumOfTMPPlotPts:]))
            self.ax_tmp_ch_7.set_ylim(min(self.tmp_ch_7[-self.NumOfTMPPlotPts:]) - 0.01,
                                      max(self.tmp_ch_7[-self.NumOfTMPPlotPts:]) + 0.01)
            self.ax_tmp_ch_7.yaxis.label.set_color('blue')
            # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            # self.myXLabel = mdates.DateFormatter("%H:%M")
            self.ax_tmp_ch_7.xaxis.set_major_formatter(self.myXLabel)
            plt.setp(self.ax_tmp_ch_7.get_xticklabels(), fontsize=8, visible=False)
            plt.setp(self.ax_tmp_ch_7.get_yticklabels(), fontsize=8, rotation='horizontal')
            self.tmp_ch_7_Figure.canvas.draw()
            self.tmp_ch_7_Figure.canvas.flush_events()

        # -- Update figure tmp_ch_8 --
        #if self.ch_tmp_en_ch_8.isChecked():
        self.ax_tmp_ch_8.clear()
        if self.ch_tmp_en_ch_8.isChecked():
            self.tmp_ch8_line, = self.ax_tmp_ch_8.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                        self.tmp_ch_8[-self.NumOfTMPPlotPts:],
                                                        color='#eb0766', linestyle='solid', label='TMP_TP_6', linewidth=1)
            self.ax_tmp_ch_8.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
        else:
            self.tmp_ch8_line, = self.ax_tmp_ch_8.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                       self.tmp_ch_8[-self.NumOfTMPPlotPts:],
                                                       color='white', linestyle='solid', label='TMP_TP_6',
                                                       linewidth=1)
        self.ax_tmp_ch_8.set_xlabel('Time', FontSize=9, Family='Century Gothic', color='b')
        self.ax_tmp_ch_8.grid(c='k', ls='--', lw=0.1)
        self.ax_tmp_ch_8.set_facecolor('w')
        self.ax_tmp_ch_8.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                    max(self.DateTime[-self.NumOfTMPPlotPts:]))
        self.ax_tmp_ch_8.set_ylim(min(self.tmp_ch_8[-self.NumOfTMPPlotPts:]) - 0.01,
                                    max(self.tmp_ch_8[-self.NumOfTMPPlotPts:]) + 0.01)
        self.ax_tmp_ch_8.yaxis.label.set_color('blue')
        # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        # self.myXLabel = mdates.DateFormatter("%H:%M")
        self.ax_tmp_ch_8.xaxis.set_major_formatter(self.myXLabel)
        plt.setp(self.ax_tmp_ch_8.get_xticklabels(), fontsize=8, visible=True)
        plt.setp(self.ax_tmp_ch_8.get_yticklabels(), fontsize=8, rotation='horizontal')
        self.tmp_ch_8_Figure.canvas.draw()
        self.tmp_ch_8_Figure.canvas.flush_events()


        # -- Update figure tmp_all --
        mint, maxt = OWENReader.MinMaxValues(
            [self.tmp_ch_1[-self.NumOfTMPPlotPts:], self.tmp_ch_2[-self.NumOfTMPPlotPts:],
             self.tmp_ch_3[-self.NumOfTMPPlotPts:], self.tmp_ch_4[-self.NumOfTMPPlotPts:],
             self.tmp_ch_5[-self.NumOfTMPPlotPts:], self.tmp_ch_6[-self.NumOfTMPPlotPts:],
             self.tmp_ch_7[-self.NumOfTMPPlotPts:], self.tmp_ch_8[-self.NumOfTMPPlotPts:]])

        self.ax_tmp_all.clear()
        self.tmp_all_line_t1, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                   self.tmp_ch_1[-self.NumOfTMPPlotPts:],
                                                   color='b', linestyle='solid', label=self.ChannelNames.get("Channel 1"), linewidth=1)

        self.tmp_all_line_t2, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_2[-self.NumOfTMPPlotPts:],
                                                     color='#4fffff', linestyle='solid', label=self.ChannelNames.get("Channel 2"), linewidth=1)

        self.tmp_all_line_t3, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_3[-self.NumOfTMPPlotPts:],
                                                     color='r', linestyle='solid', label=self.ChannelNames.get("Channel 3"), linewidth=1)

        self.tmp_all_line_t4, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_4[-self.NumOfTMPPlotPts:],
                                                     color='#ff00fb', linestyle='solid', label=self.ChannelNames.get("Channel 4"), linewidth=1)

        self.tmp_all_line_t5, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_5[-self.NumOfTMPPlotPts:],
                                                     color='#00FF00', linestyle='solid', label=self.ChannelNames.get("Channel 5"), linewidth=1)

        self.tmp_all_line_t6, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_6[-self.NumOfTMPPlotPts:],
                                                     color='#f5d311', linestyle='solid', label=self.ChannelNames.get("Channel 6"), linewidth=1)

        self.tmp_all_line_t7, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_7[-self.NumOfTMPPlotPts:],
                                                     color='#b700ff', linestyle='solid', label=self.ChannelNames.get("Channel 7"), linewidth=1)

        self.tmp_all_line_t8, = self.ax_tmp_all.plot(self.DateTime[-self.NumOfTMPPlotPts:],
                                                     self.tmp_ch_8[-self.NumOfTMPPlotPts:],
                                                     color='#eb0766', linestyle='solid', label=self.ChannelNames.get("Channel 8"), linewidth=1)

        self.ax_tmp_all.legend(loc='best')
        self.ax_tmp_all.set_ylabel("t, " + "\u00b0" + "C", FontSize=9, Family='Century Gothic')
        self.ax_tmp_all.set_xlabel('Time', FontSize=9, Family='Century Gothic', color='b')
        self.ax_tmp_all.grid(c='k', ls='--', lw=0.1)
        self.ax_tmp_all.set_facecolor('w')
        self.ax_tmp_all.set_xlim(min(self.DateTime[-self.NumOfTMPPlotPts:]),
                                  max(self.DateTime[-self.NumOfTMPPlotPts:]))
        self.ax_tmp_all.set_ylim(mint - 0.01, maxt + 0.01)
        self.ax_tmp_all.yaxis.label.set_color('blue')
        # self.ax_tmp_ch_2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        # self.myXLabel = mdates.DateFormatter("%H:%M")
        self.ax_tmp_all.xaxis.set_major_formatter(self.myXLabel)
        plt.setp(self.ax_tmp_all.get_xticklabels(), fontsize=8, visible=True)
        plt.setp(self.ax_tmp_all.get_yticklabels(), fontsize=8, rotation='horizontal')
        self.tmp_all_Figure.canvas.draw()
        self.tmp_all_Figure.canvas.flush_events()
    def Update_TMP_lbl(self):
        if self.ch_tmp_en_ch_1.isChecked():
            self.lbl_act_tmp_ch_1.setText(str("{0:.1f}".format(self.tmp_ch_1[-1])))
        if self.ch_tmp_en_ch_2.isChecked():
            self.lbl_act_tmp_ch_2.setText(str("{0:.1f}".format(self.tmp_ch_2[-1])))
        if self.ch_tmp_en_ch_3.isChecked():
            self.lbl_act_tmp_ch_3.setText(str("{0:.1f}".format(self.tmp_ch_3[-1])))
        if self.ch_tmp_en_ch_4.isChecked():
            self.lbl_act_tmp_ch_4.setText(str("{0:.1f}".format(self.tmp_ch_4[-1])))
        if self.ch_tmp_en_ch_5.isChecked():
            self.lbl_act_tmp_ch_5.setText(str("{0:.1f}".format(self.tmp_ch_5[-1])))
        if self.ch_tmp_en_ch_6.isChecked():
            self.lbl_act_tmp_ch_6.setText(str("{0:.1f}".format(self.tmp_ch_6[-1])))
        if self.ch_tmp_en_ch_7.isChecked():
            self.lbl_act_tmp_ch_7.setText(str("{0:.1f}".format(self.tmp_ch_7[-1])))
        if self.ch_tmp_en_ch_8.isChecked():
            self.lbl_act_tmp_ch_8.setText(str("{0:.1f}".format(self.tmp_ch_8[-1])))
    def Update_TMP_Track_lbl(self):
        self.lbl_tmp_ch_1_track.setText(str("{0:.1f}".format(self.tmp_ch_1[-1])))
        self.lbl_tmp_ch_2_track.setText(str("{0:.1f}".format(self.tmp_ch_2[-1])))
        self.lbl_tmp_ch_3_track.setText(str("{0:.1f}".format(self.tmp_ch_3[-1])))
        self.lbl_tmp_ch_4_track.setText(str("{0:.1f}".format(self.tmp_ch_4[-1])))
        self.lbl_tmp_ch_5_track.setText(str("{0:.1f}".format(self.tmp_ch_5[-1])))
        self.lbl_tmp_ch_6_track.setText(str("{0:.1f}".format(self.tmp_ch_6[-1])))
        self.lbl_tmp_ch_7_track.setText(str("{0:.1f}".format(self.tmp_ch_7[-1])))
        self.lbl_tmp_ch_8_track.setText(str("{0:.1f}".format(self.tmp_ch_8[-1])))


# Work with log-giles
    def ChooseLogFile(self):
        rec_filename = "OwenTemp_" + str(datetime.now().strftime("%Y_%m_%d"))
        options = QtWidgets.QFileDialog.Options()
        self.LogPath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save To File", rec_filename, "OwenTemp Log Files (*.log)", options=options)
        if self.LogPath:
            TmpToFile.WriteHeading(self.LogPath)
            self.ch_save_to_file.setEnabled(True)
            self.lbl_ed_logpath.setEnabled(True)
            self.lbl_ed_logpath.setText(str(self.LogPath))
        else:
            self.ch_save_to_file.setDisabled(True)
            self.lbl_ed_logpath.setDisabled(True)
            self.lbl_ed_logpath.clear()
    def LogToFileCheck(self):
        if self.ch_save_to_file.isChecked():
            self.lbl_ed_logpath.setDisabled(True)
            self.bth_create_logfile.setDisabled(True)
        else:
            self.lbl_ed_logpath.setEnabled(True)
            self.bth_create_logfile.setEnabled(True)

    def UpdateDateTime(self):
        while True:
            self.lbl_date.setText(str(datetime.now().strftime("%d %B %Y")))
            self.lbl_time.setText(str(datetime.now().strftime("%H:%M:%S")))
            sleep(1)

    def UpdateTable(self):
        self.RowCnt = self.RowCnt + 1
        self.tableI_tmp.setRowCount(self.RowCnt)
        #self.tableI_tmp.setCurrentCell(self.RowCnt-1, 0)

        d = QtWidgets.QTableWidgetItem((self.DateTime[-1]).strftime("%H:%M:%S"))
        t1 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_1[-1]))))
        t2 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_2[-1]))))
        t3 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_3[-1]))))
        t4 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_4[-1]))))
        t5 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_5[-1]))))
        t6 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_6[-1]))))
        t7 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_7[-1]))))
        t8 = QtWidgets.QTableWidgetItem(str(("{0:.1f}".format(self.tmp_ch_8[-1]))))

        self.tableI_tmp.setItem(self.RowCnt-1, 0, d)
        self.tableI_tmp.setItem(self.RowCnt-1, 1, t1)
        self.tableI_tmp.setItem(self.RowCnt-1, 2, t2)
        self.tableI_tmp.setItem(self.RowCnt-1, 3, t3)
        self.tableI_tmp.setItem(self.RowCnt-1, 4, t4)
        self.tableI_tmp.setItem(self.RowCnt-1, 5, t5)
        self.tableI_tmp.setItem(self.RowCnt-1, 6, t6)
        self.tableI_tmp.setItem(self.RowCnt-1, 7, t7)
        self.tableI_tmp.setItem(self.RowCnt-1, 8, t8)

#Work witn siren
    def SirenCheck(self):
        if not(self.ch_sound.isChecked()):
            self.StopSiren()
        else:
            pass
    def StartAlarmThread(self):
        self.PlaySirenThread = Thread(target=self.PlaySiren)
        self.PlaySirenThread.start()
        self.PlaySirenThread.join()
    def PlaySiren(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.load('d:/shlom41k/Python/LTUTempPlot/OWEN/scripts/files/air_raid_siren.wav')
            pygame.mixer.music.play(loops=2, start=0)
            self.PlayMusicEN = True

            #clock = pygame.time.Clock()
            #clock.tick(1)
            # while self.ch_sound.isChecked():
            #     clock.tick(1)
        except:
            TmpToFile.WriteErrorToLog("Siren cant be played")
            print("Siren cant be played")
            self.PlayMusicEN = False
    def StopSiren(self):
        try:
            pygame.mixer.music.stop()
            #self.PlayMusicEN = False
        except:
            print("Siren not played")




def main():
    App = ResursSoft.QtWidgets.QApplication(sys.argv)
    OWENWindow = UIMainApp()
    OWENWindow.show()
    App.exec_()

    OWENWindow.StopCheking()
    OWENWindow.read_EN = False


if __name__ == '__main__':
    main()