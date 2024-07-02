#!/usr/bin/python3

import sys
import time
import ephem
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

moon_RA = float((25/60.0 + 59.55/3600.0) * 15)
moon_DEC = float(-3 + 1/60.0 + 4.8/3600.0)

timezone = +5.5
longitude = '80:13.7'
latitude = '26:30.6'
altitude = 123.51

moonalt_list = []
moonphase_list = []
sunalt_list = []
time_list = []
time01 = ''
time02 = ''
time03 = ''
time04 = ''

def get_4timekeys(date):
    time1 = ephem.Date(date)
    observer = ephem.Observer()
    observer.lon = longitude
    observer.lat = latitude
    observer.elevation = altitude
    observer.date = time1
    observer.horizon = '0'

    sun1 = ephem.Sun()
    sun1.compute(observer)
    sunsetting = ephem.localtime(observer.next_setting(sun1))
    t1 = str(sunsetting)
    if len(t1) > 20:
        t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f")
    else:
        t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")

    timekey1 = int(time.mktime(t1.timetuple()))
    timekey1 = int(timekey1 / 60) * 60

    sunrising = ephem.localtime(observer.next_rising(sun1))
    t2 = str(sunrising)
    if len(t2) > 20:
        t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S.%f")
    else:
        t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    timekey2 = int(time.mktime(t2.timetuple()))
    timekey2 = int(timekey2 / 60) * 60

    observer.horizon = '-13'
    sun2 = ephem.Sun()
    sun2.compute(observer)
    sunsetting = ephem.localtime(observer.next_setting(sun2))
    t3 = str(sunsetting)
    if len(t3) > 20:
        t3 = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S.%f")
    else:
        t3 = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S")
    timekey3 = int(time.mktime(t3.timetuple()))
    timekey3 = int(timekey3 / 60) * 60

    sunrising = ephem.localtime(observer.next_rising(sun2))
    t4 = str(sunrising)
    if len(t4) > 20:
        t4 = datetime.strptime(t4, "%Y-%m-%d %H:%M:%S.%f")
    else:
        t4 = datetime.strptime(t4, "%Y-%m-%d %H:%M:%S")
    timekey4 = int(time.mktime(t4.timetuple()))
    timekey4 = int(timekey4 / 60) * 60

    return timekey1, timekey2, timekey3, timekey4

def get_sunmoon_alt(date):
    time = ephem.Date(date)
    observer = ephem.Observer()
    observer.lon = longitude
    observer.lat = latitude
    observer.elevation = altitude
    observer.date = time

    sun = ephem.Sun()
    sun.compute(observer)
    sun_alt = str(sun.alt)

    moon = ephem.Moon()
    moon.compute(observer)
    moon_alt = str(moon.alt)
    moon_phase = moon.phase

    return sun_alt, moon_alt, moon_phase

def get_star_alt(date, ra, dec):
    time = ephem.Date(date)
    observer = ephem.Observer()
    observer.lon = longitude
    observer.lat = latitude
    observer.elevation = altitude
    observer.date = time

    star = ephem.FixedBody()
    star._ra = ra
    star._dec = dec
    star.compute(observer)
    alt = str(star.alt)

    moon = ephem.Moon(time)
    s = str(ephem.separation(star, moon))

    return alt, s

def isValidDate(str):
    try:
        time.strptime(str, "%Y-%m-%d %H:%M:%S")
        return True
    except:
        return False

def plotbar(date0, date1, size, obj_list, staralt_list, moondist_list, offset_str, gmtime_str, localtime_str, twilight01, twilight02):
    n = size
    x = np.arange(n)
    plt.figure(figsize=(9, 8))
    ax1 = plt.subplot(111)
    ax1.set_xlabel("Local Time (UTC+05:30)")
    ax1.set_ylabel(r"Altitude / $^{\circ}$")
    ax1.set_ylim(0, 90)
    ax1.set_xlim(0, n)
    ax1.set_yticks(np.arange(0, 100, 10))
    ax1.set_yticklabels(('0', '10', '20', '30', '40', '50', '60', '70', '80', '90'))
    ax1.set_xticks(offset_str)
    ax1.set_xticklabels(localtime_str)

    c01 = 'purple'
    line1 = ax1.axvline(twilight01, color=c01, linewidth=1)
    line1.set_dashes([6, 2])
    ax1.text(twilight01 - 20, 91, time03, color=c01, size=8)
    ax1.text(twilight01 - 20, 93, 'start', color=c01, size=8)
    line2 = ax1.axvline(twilight02, color=c01, linewidth=1)
    line2.set_dashes([6, 2])
    ax1.text(twilight02 - 20, 91, time04, color=c01, size=8)
    ax1.text(twilight02 - 20, 93, 'stop', color=c01, size=8)

    c02 = 'gray'
    ax1.text(-20, 91, time01, color=c02, size=8)
    ax1.text(-20, 93, 'sunset', color=c02, size=8)
    ax1.text(n - 20, 91, time02, color=c02, size=8)
    ax1.text(n - 20, 93, 'sunrise', color=c02, size=8)

    ax1.plot(x, moonalt_list, linestyle='--', color='red', label='moon', linewidth=2)
    color_list = ['indigo', 'blue', 'cyan', 'green', 'olive', 'orange', 'tan', 'darkorange', 'tan', 'maroon']
    for i in range(len(obj_list[:][:])):
        ax1.plot(x, staralt_list[i][:], color=color_list[i], label=obj_list[i][0], linewidth=2)
        for xi, yi in zip(x, staralt_list[i]):
            if xi % 120 == 0 and yi > 0:
                ax1.text(xi + 15, yi, '{}'.format(moondist_list[i][xi]), color=color_list[i])

    phase1 = moonphase_list[0]
    phase2 = moonphase_list[-1]
    plt.title('{} @ Observatory'.format(date0), y=1.05)
    ax1.text(int(n / 2) - 100, 91, 'moonphase: {:.2f}~{:.2f}%'.format(phase1, phase2), color='red', size=8)
    ax1.plot(x, [20] * n, color=c01, linewidth=1)
    ax1.text(n + 10, 19, 'alt_limit', color=c01)
    ax1.text(n + 10, 10, "Numbers below curves", size=6, color=c01)
    ax1.text(n + 10, 8, "are Moon distance", size=6, color=c01)
    ax1.text(n + 20, 0, "Created by: xyx", size=10, color=c02)
    plt.legend(loc=2, bbox_to_anchor=(1.03, 0.95), borderaxespad=0)
    plt.subplots_adjust(right=0.75)
    plt.grid()
    plt.show()

def alt2alt(ori_alt):
    alt_array = ori_alt.split(':')
    alt_d = float(alt_array[0])
    alt_m = float(alt_array[1]) / 60.0
    alt_s = float(alt_array[2]) / 3600.0
    alt = 0.0
    if ori_alt[0] == '-':
        alt = round(alt_d - alt_m - alt_s, 2)
    else:
        alt = round(alt_d + alt_m + alt_s, 2)
    return alt

def run():
    argc = len(sys.argv)
    flag = 0
    nYear = 0
    nMonth = 0
    nDay = 0
