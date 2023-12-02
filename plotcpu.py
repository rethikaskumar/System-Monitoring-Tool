# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:42:11 2023

@author: DELL

"""

import time
import psutil
import matplotlib.pyplot as plt
import datetime


#x=[datetime.datetime.now()+datetime.timedelta(seconds=i) for i in range(10)]
x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
cpu=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


#figure, ax = plt.subplots(figsize=(10, 8))

plt.ion()
figure=plt.figure()
ax=figure.add_subplot(111)
#ax.set(xlabel=None)
ax.set_xticklabels([])

line1, = ax.plot(x, cpu, 'b-')
ax.set_xlim([0, 9])
ax.set_ylim([0, 100])

while(1):
    cpu.append(psutil.cpu_percent(1))
    cpu=cpu[1:]
    #ax.set_xlim([datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(seconds=9)])
    line1.set_xdata(x)
    line1.set_ydata(cpu)
    figure.canvas.draw()
    figure.canvas.flush_events()
    time.sleep(0.1)
    
plt.show()


