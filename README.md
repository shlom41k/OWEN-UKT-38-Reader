# OWEN-UKT-38-Reader
Desctop aplication for work with [UKT-38](https://owen.ru/product/ukt38) device.
<hr>

## Main tools:
```
- python 3.10.2
- matplotlib 3.5.1
- pyQt5 5.15.6
- pyserial 3.5
- pySide2 5.15.2.1
```

## Description:
The application allows:
- read data from the device via COM port (protocol description see [here](https://github.com/shlom41k/OWEN-UKT-38-Reader/tree/main/src/files/%D0%A3%D0%9A%D0%A2));
- display instrument readings in the form of graphs;
- save data to log files;
- signal when the readings exceed the set limits.

## Running application:
- ```python -m pip install -r requirements.txt```
- ```python .\MainUIApp.py ```
<hr>

## Main window:
<p align="center">
  <img src="https://github.com/shlom41k/OWEN-UKT-38-Reader/blob/main/src/files/main.PNG">
</p>
