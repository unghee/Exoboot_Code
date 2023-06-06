import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate
import constants

folder = 'exo_data/'
# for filename in ["20220210_1440_calibration2_LEFT.csv"]:
# for filename in ["20220216_1229_calibration2_LEFT.csv"]:
for filename in ["20230602_1845_calibration_2_2ndJUne_RIGHT.csv"]:
    with open(folder + filename) as f:
        motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
    with open(folder + filename) as f:
        ankle_angle = [
            np.floor(float(row["ankle_angle"])) for row in csv.DictReader(f)
        ]
    motor_angle = np.array(motor_angle) * constants.ENC_CLICKS_TO_DEG

    # Sort the data points
    zipped_sorted_lists = sorted(zip(ankle_angle, motor_angle))
    mytuples = zip(*zipped_sorted_lists)
    ankle_angle, motor_angle = [list(mytuple) for mytuple in mytuples]
    # Filter
    b, a = signal.butter(N=1, Wn=0.05)
    motor_angle = signal.filtfilt(b, a, motor_angle, method="gust")
    ankle_angle = signal.filtfilt(b, a, ankle_angle, method="gust")

    # Polyfit
    p = np.polyfit(ankle_angle,
                   motor_angle / constants.ENC_CLICKS_TO_DEG,
                   deg=5)
    print('Polynomial coefficients: ', p)

    p_deg = np.polyfit(ankle_angle, motor_angle, deg=5)

    polyfitted_left_motor_angle = np.polyval(p_deg, ankle_angle)

    plt.figure(1)
    plt.xlabel('ankle angle')
    plt.ylabel('motor angle')

    plt.plot(ankle_angle, motor_angle)
    plt.plot(ankle_angle, polyfitted_left_motor_angle, linestyle='dashed')

    plt.figure(2)
    p_deriv = np.polyder(p_deg)
    print('Polynomial deriv coefficients: ', p_deriv)

    TR_from_polyfit = np.polyval(p_deriv, ankle_angle)
    plt.plot(ankle_angle, -TR_from_polyfit, label="polyfit")

    TR_from_ankle_angle = interpolate.PchipInterpolator(
        ankle_angle, TR_from_polyfit)

    plt.plot(ankle_angle,
             TR_from_ankle_angle(ankle_angle),
             linewidth=5,
             label="pchip auto"
             )  #Multiply -1 to TR_from-ankle_angle(ankle_angle) for Left

    #RIGHT
    ankle_pts = np.array([
        -67, -60, -50, -40, -20, -10, 0, 10, 20, 30, 40, 45.6, 55, 70, 80, 86
    ])
    deriv_pts = np.array([
        15.5, 13.35, 11.95, 12.03, 13.82, 14.3, 13.96, 12.77, 10.56, 7.1, 3.19,
        0.66, -3.78, -9.55, -12.58, -13.09
    ])

    #LEFT
    #ankle_pts = np.array([-67, -60, -47,-40, -20, -10 ,0, 10, 20, 30, 40, 45.6, 55, 80, 90, 100, 112])
    #deriv_pts = np.array([14.85, 14, 11.89, 12.74, 14.28, 13.71, 12.54, 10.43, 8, 5.5, 2.3, 0.4, -3.3, -10, -11.30, -10.95, -8.75])

    #DEFAULT
    #ankle_pts = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
    #deriv_pts = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5, -11 ])

    deriv_spline_fit = interpolate.pchip_interpolate(ankle_pts, deriv_pts,
                                                     ankle_angle)

    plt.plot(ankle_angle, deriv_spline_fit, linewidth=5, label="pchip manual")
    plt.legend()
    plt.ylabel('Transmission Ratio')
    plt.xlabel('Ankle Angle')

    motor_torque = constants.MAX_ALLOWABLE_CURRENT_COMMAND * constants.MOTOR_CURRENT_TO_MOTOR_TORQUE

    ankle_torque = motor_torque * \
        np.polyval(p_deriv, ankle_angle[50])

plt.show()