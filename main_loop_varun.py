import exoboot
import threading
import controllers
import state_machines
import gait_state_estimators
import constants
import filters
import time
import util
import config_util
import parameter_passers
import control_muxer
import plotters
import ml_util
import traceback

import ControllerCommunication

import scipy.signal
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt


config = config_util.load_config_from_args()  # loads config from passed args
file_ID = input(
    'Other than the date, what would you like added to the filename?')

'''if sync signal is used, this will be gpiozero object shared between exos.'''
sync_detector = config_util.get_sync_detector(config)

'''Connect to Exos, instantiate Exo objects.'''
exo_list = exoboot.connect_to_exos(
    file_ID=file_ID, config=config, sync_detector=sync_detector)
print('Battery Voltage: ', 0.001*exo_list[0].get_batt_voltage(), 'V')

config_saver = config_util.ConfigSaver(
    file_ID=file_ID, config=config)  # Saves config updates

'''Instantiate gait_state_estimator and state_machine objects, store in lists.'''
gait_state_estimator_list, state_machine_list = control_muxer.get_gse_and_sm_lists(
    exo_list=exo_list, config=config)

'''Prep parameter passing.'''
lock = threading.Lock()
quit_event = threading.Event()
new_params_event = threading.Event()
# v0.2,15,0.56,0.6!

'''Perform standing calibration.'''
if not config.READ_ONLY:
    for exo in exo_list:
        standing_angle = exo.standing_calibration(config=config)
        if exo.side == constants.Side.LEFT:
            config.LEFT_STANDING_ANGLE = standing_angle
        else:
            config.RIGHT_STANDING_ANGLE = standing_angle
else:
    print('Not calibrating... READ_ONLY = True in config')

input('Press any key to begin')
print('Start!')

'''Main Loop: Check param updates, Read data, calculate gait state, apply control, write data.'''
timer = util.FlexibleTimer(
    target_freq=config.TARGET_FREQ)  # attempts constants freq
t0 = time.perf_counter()
#keyboard_thread = parameter_passers.ParameterPasser(lock=lock, config=config, quit_event=quit_event,new_params_event=new_params_event)

communication_thread = ControllerCommunication.ControllerCommunication(config=config, exo_list=exo_list, new_params_event = new_params_event)

config_saver.write_data(loop_time=0)  # Write first row on config
only_write_if_new = not config.READ_ONLY and config.ONLY_LOG_IF_NEW
for exo in exo_list:
    exo.read_data(config)
t0_state_time = exo.data.state_time

heel_strike_counter = 0
t_1  = []
t_2  = []
temp_ankle_angle = []
temp_ankle_angular_velocity = []
while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        lock.acquire()
        if new_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            for state_machine in state_machine_list:  # Make sure up to date
                state_machine.update_ctrl_params_from_config(config=config)
            for gait_state_estimator in gait_state_estimator_list:  # Make sure up to date
                gait_state_estimator.update_params_from_config(config=config)
            new_params_event.clear()
        if quit_event.is_set():  # If user enters "quit"
            break
        lock.release()

        for exo in exo_list:
            exo.read_data(config=config,loop_time=loop_time)
        for gait_state_estimator in gait_state_estimator_list:
            gait_state_estimator.detect()
            """t = gait_state_estimator.detect()
            if(heel_strike_counter >= 1):
                t_1.append(exo.data.ankle_angle)
                t_2.append(exo.data.ankle_velocity)
            if(t == True): #Uncomment for actual runnning
                heel_strike_counter += 1
                if(heel_strike_counter % 2 == 0):
                    print(len(t_1))
                    print(len(t_2))
                    temp_ankle_angle.append(scipy.signal.resample(t_1,500)) #I have selected 500, I need to tune it!!!!
                    temp_ankle_angular_velocity.append(scipy.signal.resample(t_2, 500))
                    t_1 = []
                    t_2 = []
                if(heel_strike_counter % 10 == 0):
                    temp_ankle_angle = np.array(temp_ankle_angle).sum(axis=0) / 5
                    temp_ankle_angular_velocity = np.array(temp_ankle_angular_velocity).sum(axis=0) / 5
                    communication_thread.sending_data(temp_ankle_angle, temp_ankle_angular_velocity) #ToDo take care of two Exo
                    temp_ankle_angle = []
                    temp_ankle_angular_velocity = []
                    print("Outside the loop")"""
        #print("further outside...")
        if not config.READ_ONLY:
            for state_machine in state_machine_list:
                state_machine.step(read_only=config.READ_ONLY)
        for exo in exo_list:
            exo.write_data(config=config,only_write_if_new=only_write_if_new)
            print("Exo torque", exo.data.ankle_torque_from_current)

        """if (int(loop_time % 20) == 0):
            print("Loop TIme", loop_time)
            print("State_Time",exo.data.state_time - t0_state_time)"""
        #time.sleep(5)
        """if(communication_thread.action_received == True):
            print("Action received true")"""
        """for exo in exo_list:
            exo.sending_data(config)"""
        """print(config.sending_ankle_angle)
        print(config.sending_ankle_velocity)
        time.sleep(0.2)"""
    except KeyboardInterrupt:
        print('Ctrl-C detected, Exiting Gracefully')
        break
    except Exception as err:
        print(traceback.print_exc())
        print("Unexpected error:", err)
        break