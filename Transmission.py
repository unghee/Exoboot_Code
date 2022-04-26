import csv

import constants
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate
import constants

folder = 'exo_data/'

for filename in ["20220425_2352_calibration2_LEFT.csv"]:
    with open(folder + filename) as f:
        motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
    with open(folder + filename) as f:
        ankle_angle = [
            np.floor(float(row["ankle_angle"])) for row in csv.DictReader(f)
        ]
    motor_angle = np.array(motor_angle) * constants.ENC_CLICKS_TO_DEG

    # Sort the data points
    zipped_sorted_lists = zip(ankle_angle, motor_angle)
    mytuples = zip(*zipped_sorted_lists)
    ankle_angle, motor_angle = [list(mytuple) for mytuple in mytuples]
    # Filter
    b, a = signal.butter(N=1, Wn=0.05)
    motor_angle = signal.filtfilt(b, a, motor_angle, method="gust")
    ankle_angle = signal.filtfilt(b, a, ankle_angle, method="gust")

    ankle_pts = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
    deriv_pts = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5,
                          -11])  # Nm/Nm


    temp_left = []
    for i in range(50,250):
        temp_left.append(ankle_angle[i])
    
    #print(ankle_angle)
    print("Average Ankle Angle Left", np.mean(temp_left))

for filename in ["20220425_2353_calibration2_RIGHT.csv"]:
    with open(folder + filename) as f:
        motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
    with open(folder + filename) as f:
        ankle_angle = [
            np.floor(float(row["ankle_angle"])) for row in csv.DictReader(f)
        ]
    motor_angle = np.array(motor_angle) * constants.ENC_CLICKS_TO_DEG

    # Sort the data points
    zipped_sorted_lists = zip(ankle_angle, motor_angle)
    mytuples = zip(*zipped_sorted_lists)
    ankle_angle, motor_angle = [list(mytuple) for mytuple in mytuples]
    # Filter
    b, a = signal.butter(N=1, Wn=0.05)
    motor_angle = signal.filtfilt(b, a, motor_angle, method="gust")
    ankle_angle = signal.filtfilt(b, a, ankle_angle, method="gust")

    ankle_pts = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
    deriv_pts = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5,
                          -11])  # Nm/Nm


    temp_right = []
    for i in range(50,250):
        temp_right.append(ankle_angle[i])
    
    #print(ankle_angle)
    print("Average Ankle Angle Right", np.mean(temp_right))
