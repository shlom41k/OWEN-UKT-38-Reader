# -*- coding: utf-8 -*-

import json
import os

ChannelNames = {
    'Channel 1': 'Enter channel name',
    'Channel 2': 'Enter channel name',
    'Channel 3': 'Enter channel name',
    'Channel 4': 'Enter channel name',
    'Channel 5': 'Enter channel name',
    'Channel 6': 'Enter channel name',
    'Channel 7': 'Enter channel name',
    'Channel 8': 'Enter channel name'
}

scriptpath = os.path.abspath(os.path.dirname(__file__))
savepath = os.path.join(scriptpath, "files\\ChannelNames.json")

def SaveChannelNames(Names, path=savepath):
    with open(path, 'w') as fid:
        json.dump(Names, fid, ensure_ascii=False, indent=4)

def LoadChannelNames(path=savepath):
    with open(path, 'r') as fid:
        Names = json.load(fid)
    return Names


if __name__ == "__main__":
    SaveChannelNames(ChannelNames)
    Names = LoadChannelNames()
    print(Names)

