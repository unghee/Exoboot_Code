import os
import sys
import exoboot
import time
import csv
import util
import constants
import config_util
import numpy as np

def calibrate_encoder_to_ankle_conversion(c,exo: exoboot.Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
                     Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)
    # exo.command_current(exo.motor_sign*1000)
    print('begin!')
    temp_ankle_angle_array = []
    for _ in range(1000):
        exo.command_current(exo.motor_sign*1000)
        time.sleep(0.02)
        exo.read_data(c)
        temp_ankle_angle_array.append(exo.data.ankle_angle)
        print("ankle_angle",exo.data.ankle_angle)
        exo.write_data(c,False)
    print('Done! File saved.')
    print("Mean_ankle_angle",np.mean(temp_ankle_angle_array))


if __name__ == '__main__':
    config = config_util.load_config_from_args() 
    exo_list = exoboot.connect_to_exos(file_ID='calibration2_2ndJune',config=config)
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration(config)
    calibrate_encoder_to_ankle_conversion(config,exo=exo)
    exo.close()