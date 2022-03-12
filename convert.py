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

import numpy as np
import cv2
import pandas
import os
import datetime

### USER INPUT ######################################
file_name = 'Samstagmorgen.avi'
left = 110
right = 150
top = 50
bottom = 80
#####################################################

cap = cv2.VideoCapture(file_name)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

means = []
for i in range(frame_count):
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    crop = gray[top:bottom, left:right]
    mean = np.mean(crop.flatten())
    means.append(mean)
    if i % 1000 == 0:
        print(f'Pass 1: {i / frame_count:.0%}   ', end="\r")
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()

lower_levels = np.zeros(frame_count, np.float)
upper_levels = np.zeros(frame_count, np.float)
for i in range(frame_count):
    slice = means[max(0, i-1000):min(frame_count-1, i+1000)]
    lower_levels[i] = np.percentile(slice, 4)
    upper_levels[i] = np.percentile(slice, 70)
    if i % 1000 == 0:
        print(f'Pass 2: {i / frame_count:.0%}   ', end="\r")

load_profile = []
signal_test = [0] * frame_count
frame_of_previous_pulse = -1
state = True
for i in range(frame_count):
    if means[i] < lower_levels[i]:
        if state: # i.e., we have a downward flank
            signal_test[i] = 1
            if frame_of_previous_pulse == -1:
                load_profile.extend([float('nan')] * i)
            else:
                time_difference = i - frame_of_previous_pulse
                load_profile.extend([1000 * 3600 / (75 * time_difference)] * time_difference)
            frame_of_previous_pulse = i
            state = False
    elif means[i] > upper_levels[i]:
        state = True

assert len(load_profile) == frame_of_previous_pulse, 'Error when building load profile'
load_profile.extend([float('nan')] * (frame_count - frame_of_previous_pulse))

timestamps = []
end_time = os.path.getmtime(file_name)
for i in range(frame_count):
    dt = datetime.datetime.fromtimestamp(end_time - frame_count + i + 1)
    s = dt.strftime('%Y-%m-%d %H:%M:%S')
    timestamps.append(s)

df1 = pandas.DataFrame(data={'Grayscale Mean': means, 'Lower': lower_levels, 'Upper': upper_levels, 'Signal Test': signal_test})
df1.to_csv(file_name + "_diagnostics.csv", sep=';', index=False, na_rep='')

df2 = pandas.DataFrame(data={'Timestamp' : timestamps, 'Load': load_profile})
df2.to_csv(file_name + ".csv", sep=';', index=False, na_rep='')