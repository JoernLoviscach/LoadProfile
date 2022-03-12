#    Copyright (C) 2022 Jörn Loviscach <https://j3L7h.de>
#
#    This file is part of LoadProfile.
#
#    LoadProfile is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    LoadProfile is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with LoadProfile.  If not, see <https://www.gnu.org/licenses/>.

import os
import pandas
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as tck

### USER INPUT ######################################
# to account for the power usage of the computer
# used for measuring
power_correction = 60 # Watts
#####################################################

files = [f for f in os.listdir() if f.endswith("avi.csv")]
number_of_files = len(files)
sum_of_load_of_hour_of_day = np.zeros(24)
number_of_measurements_for_hour_of_day = np.zeros(24)

for i in range(number_of_files):
    print(files[i])
    df = pandas.read_csv(files[i], sep=';', na_values='', keep_default_na=False, parse_dates=[0], infer_datetime_format=True)
    # print(df.info)
    x = []
    y = []
    for _, timestamp, load in df.itertuples():
        ts = pandas.Timestamp(timestamp)
        hours = ts.hour
        seconds = (ts.hour * 60 + ts.minute) * 60 + ts.second
        if not math.isnan(load):
            corrected_load = load - power_correction
            sum_of_load_of_hour_of_day[hours] += corrected_load
            number_of_measurements_for_hour_of_day[hours] += 1
            x.append(seconds / (60 * 60))
            y.append(corrected_load)
    plt.scatter(x, y, marker='.', s=0.5, lw=0)

load_of_hour_of_day = sum_of_load_of_hour_of_day / number_of_measurements_for_hour_of_day

plt.hlines(load_of_hour_of_day, np.arange(24), np.arange(start=1, stop=25))

av = np.average(load_of_hour_of_day)
plt.hlines(av, 0, 24, colors='r')

breakpoint = 500
shrink_factor = 10
def forward(y):
    return np.where(y < breakpoint, y, breakpoint + (y - breakpoint) / shrink_factor)
def inverse(y):
    return np.where(y < breakpoint, y, breakpoint + (y - breakpoint) * shrink_factor)

plt.xlabel('Time of Day / h')
plt.xlim(0, 24)
plt.gca().get_xaxis().set_major_locator(tck.FixedLocator([0, 4, 8, 12, 16, 20, 24]))
plt.gca().get_xaxis().set_major_formatter(tck.FixedFormatter(['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00']))

plt.ylabel('Load / W')
plt.ylim(0, 4000)
plt.gca().set_yscale('function', functions=(forward, inverse))
plt.gca().get_yaxis().set_major_locator(tck.FixedLocator([0, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000]))
plt.gca().get_yaxis().set_minor_locator(tck.FixedLocator([50, 150, 250, 350, 450, 750, 1250, 1500, 1750, 2250, 2500, 2750, 3250, 3500, 3750]))

plt.show()