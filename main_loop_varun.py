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

#Real-time plotting
from rtplot import client
import math

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

heel_strike_counter_left = 0
t_1_left  = []
t_2_left  = []
temp_ankle_angle_left = []
temp_ankle_angular_velocity_left = []

heel_strike_counter_right = 0
t_1_right  = []
t_2_right  = []
temp_ankle_angle_right = []
temp_ankle_angular_velocity_right = []

ankle_a_l = []
ankle_v_l = []
ankle_a_r = []
ankle_v_r = []


angle_l = []
angle_r = []

#ip address for the server -- RealTimePlotting
client.configure_ip('35.3.109.236')#("141.212.77.23")

plot_1_configs = {'names': ['Ankle Angle Left'], 'title': "Ankle Angle Left", 'colors': ['r'], 'ylabel': "degrees", 'xlabel': 'timestep'}
plot_1_1_configs = {'names': ['Ankle Angle Right'], 'title': "Ankle Angle Right", 'colors': ['m'], 'ylabel': "degrees", 'xlabel': 'timestep'}
plot_2_configs = {'names': ['Ankle Torque'], 'title': "Ankle Torque", 'colors': ['g'], 'ylabel': "Nm", 'xlabel': 'timestep'}
plot_3_configs = {'names': ['Ankle velocity'], 'title': "Ankle Velocity", 'colors': ['b'], 'ylabel': "deg/sec", 'xlabel': 'timestep'}
plot_4_configs = {'names': ['Commanded Torque'], 'title': "Commanded Torque Exoboot", 'colors': ['y'], 'ylabel': "Nm", 'xlabel': 'timestep'}
All_plots = [plot_1_configs, plot_1_1_configs, plot_2_configs, plot_4_configs, plot_3_configs]
#All_plots = [plot_2_configs]
client.initialize_plots(All_plots)
#client.initialize_plots(["Commanded Torque"])
plotting_counter = 0
left_exo_data_counter = 0
right_exo_data_counter = 0
config.action_received = True
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
            #gait_state_estimator.detect()
            t = gait_state_estimator.detect()
            for exo in exo_list:
                if(config.action_received == True and exo.side.value == 2):
                    #print("Left Exo")
                    if(heel_strike_counter_left >= 1):
                        #print("Appending the states...")
                        t_1_left.append(exo.data.ankle_angle)
                        t_2_left.append(exo.data.ankle_velocity)
                    if(t == True): #Uncomment for actual runnning
                        heel_strike_counter_left += 1
                        if(heel_strike_counter_left % 2 == 0):
                            print(len(t_1_left))
                            print(len(t_2_left))
                            temp_ankle_angle_left.append(scipy.signal.resample(t_1_left,500)) #I have selected 500, I need to tune it!!!!
                            temp_ankle_angular_velocity_left.append(scipy.signal.resample(t_2_left, 500))
                            t_1_left = []
                            t_2_left = []
                        if(heel_strike_counter_left % 9 == 0):
                            print("length",len(temp_ankle_angle_left))
                            temp_ankle_angle_left = np.delete(temp_ankle_angle_left, 0, 0) #Removing the first two steps data, as it takes a few steps for the exo to activate the desired torque
                            temp_ankle_angle_left = np.delete(temp_ankle_angle_left, 0, 0)

                            ankle_a_l = np.array(temp_ankle_angle_left).sum(axis=0) / 2
                            temp_ankle_angular_velocity_left = np.delete(temp_ankle_angular_velocity_left, 0, 0)
                            temp_ankle_angular_velocity_left = np.delete(temp_ankle_angular_velocity_left, 0, 0)

                            ankle_v_l = np.array(temp_ankle_angular_velocity_left).sum(axis=0) / 2
                            #communication_thread.sending_data(temp_ankle_angle_left, temp_ankle_angular_velocity_left, exo.side.value) #ToDo take care of two Exo
                            #config.action_received = False
                            temp_ankle_angle_left = []
                            temp_ankle_angular_velocity_left = []
                            heel_strike_counter_left = 0
                            left_exo_data_counter += 1

                if(config.action_received == True and exo.side.value == 1):
                    #print("Right Exo")
                    if(heel_strike_counter_right >= 1):
                        #print("Appending the states...")
                        t_1_right.append(exo.data.ankle_angle)
                        t_2_right.append(exo.data.ankle_velocity)
                    if(t == True): #Uncomment for actual runnning
                        heel_strike_counter_right += 1
                        if(heel_strike_counter_right % 2 == 0):
                            print(len(t_1_right))
                            print(len(t_2_right))
                            temp_ankle_angle_right.append(scipy.signal.resample(t_1_right,500)) #I have selected 500, I need to tune it!!!!
                            temp_ankle_angular_velocity_right.append(scipy.signal.resample(t_2_right, 500))
                            t_1_right = []
                            t_2_right = []
                        if(heel_strike_counter_right % 9 == 0):
                            print("length",len(temp_ankle_angle_right))
                            temp_ankle_angle_right = np.delete(temp_ankle_angle_right, 0, 0) #Removing the first two steps data, as it takes a few steps for the exo to activate the desired torque
                            temp_ankle_angle_right = np.delete(temp_ankle_angle_right, 0, 0)

                            ankle_a_r = np.array(temp_ankle_angle_right).sum(axis=0) / 2
                            temp_ankle_angular_velocity_right = np.delete(temp_ankle_angular_velocity_right, 0, 0)
                            temp_ankle_angular_velocity_right = np.delete(temp_ankle_angular_velocity_right, 0, 0)

                            ankle_v_r = np.array(temp_ankle_angular_velocity_right).sum(axis=0) / 2
                            #communication_thread.sending_data(temp_ankle_angle_right, temp_ankle_angular_velocity_right, exo.side.value) #ToDo take care of two Exo
                            #config.action_received = False
                            temp_ankle_angle_right = []
                            temp_ankle_angular_velocity_right = [] 
                            heel_strike_counter_right = 0
                            right_exo_data_counter += 1

            if(left_exo_data_counter != 0 and right_exo_data_counter != 0):
                communication_thread.sending_data(ankle_a_l, ankle_v_l, ankle_a_r, ankle_v_r)
                left_exo_data_counter = 0
                right_exo_data_counter = 0
                config.action_received = False
        #print("further outside...")
        if not config.READ_ONLY:
            for state_machine in state_machine_list:
                #print("Torque", config.torque_profile)
                state_machine.step(config = config, read_only=config.READ_ONLY)
        for exo in exo_list:
            exo.write_data(config=config,only_write_if_new=only_write_if_new)
            #RealTimePlotting
            exo.data.commanded_torque = np.asarray(exo.data.commanded_torque)
            exo.data.commanded_torque = exo.data.commanded_torque.astype(float)
            if(math.isnan(exo.data.commanded_torque)):
                t_commanded = 0
            else:
                t_commanded = exo.data.commanded_torque

            if(exo.side.value == 1):
                #print('right')
                angle_r = exo.data.ankle_angle
            elif(exo.side.value == 2):
                #print('Left')
                angle_l = exo.data.ankle_angle
            else:
                pass
            plotting_data = [angle_l, angle_r, exo.data.ankle_torque_from_current, t_commanded,exo.data.ankle_velocity]
            #plotting_data = [exo.data.ankle_torque_from_current]
            plotting_counter += 1
            if(plotting_counter%6 == 0):
                client.send_array(plotting_data)
            """t_plotting = np.asarray(config.torque_profile)
            t_plotting = t_plotting.astype(float)
            client.send_array(t_plotting)"""
            #print("Exo torque", exo.data.ankle_torque_from_current)

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