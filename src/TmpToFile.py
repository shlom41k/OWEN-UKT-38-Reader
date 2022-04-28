# -*- coding: utf-8 -*-

from datetime import datetime
import os

scriptpath = os.path.abspath(os.path.dirname(__file__))
ErrorLogPath = os.path.join(scriptpath, "files\\Errors.log")

def WriteHeading(path):
    with open(path, 'w') as file:
        file.write(str(datetime.now().strftime("%d-%B-%Y %H:%M:%S")) + "\n")
        file.write("Format: {Datetime,  T1, T2, T3, T4, T5, T6, T7, T8}" + "\n" + "\n")

def DataToFile(datetime, t1, t2, t3, t4, t5, t6, t7, t8, file, sep=", "):
    with open(file, 'a') as file:
        file.write(str(datetime)+sep+"\t"+("{0:.1f}".format(t1))+sep+("{0:.1f}".format(t2))+sep+("{0:.1f}".format(t3))+
                   sep+("{0:.1f}".format(t4))+sep+("{0:.1f}".format(t5))+sep+("{0:.1f}".format(t6))+
                   sep+("{0:.1f}".format(t7))+sep+("{0:.1f}".format(t8))+"\n")

def WriteErrorToLog(message, path=ErrorLogPath):
    with open(path, 'a') as file:
        file.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " - " + message + "\n")


if __name__ == "__main__":
    pass
    # s = mixer.Sound('d:/shlom41k/Python/LTUTempPlot/OWEN/scripts/files/Single.mp3')
    # s.play()
    #mixer.music.stop()