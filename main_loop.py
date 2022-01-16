'''
This is the main GT program for running the Dephy exos. Read the Readme.
'''
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
import communication #it contains the comunication loop
import control_muxer
import plotters
import ml_util
import traceback

from concurrent import futures
import grpc
import Message_pb2
import Message_pb2_grpc

computer_address = f"{'35.3.247.229'}:" f"{50050}" #This contains the ip address of the device running the optimizer

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


'''Perform standing calibration.'''
if not config.READ_ONLY:
    for exo in exo_list:
        standing_angle = exo.standing_calibration()
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
communication_thread = communication.ControllerCommunication(config=config)
config_saver.write_data(loop_time=0)  # Write first row on config
only_write_if_new = not config.READ_ONLY and config.ONLY_LOG_IF_NEW

'''This function gives the call to the optimizer to update the cmase {Note: even though this function 
calls the optimizer everytime the controller finishes running, the cmaes gets updated only after the 
new parameters are generated (This is logic is written in the optimizer script)}'''

def update_function():
    with grpc.insecure_channel(computer_address, options=(('grpc.enable_http_proxy', 0),)) as channel:
        stub = Message_pb2_grpc.UpdateCmaesRequestStub(channel)
        stub.UpdateRequest(Message_pb2.URequest(update_request = 'update'))
    return

while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        for exo in exo_list:
            exo.read_data(loop_time=loop_time)
        for gait_state_estimator in gait_state_estimator_list:
            gait_state_estimator.detect()
        if not config.READ_ONLY:
            for state_machine in state_machine_list:
                state_machine.step(read_only=config.READ_ONLY)
        for exo in exo_list:
            exo.write_data(only_write_if_new=only_write_if_new)
        update_function()

    except KeyboardInterrupt:
        print('Ctrl-C detected, Exiting Gracefully')
        break
    except Exception as err:
        print(traceback.print_exc())
        print("Unexpected error:", err)
        break

'''Safely close files, stop streaming, optionally saves plots'''
config_saver.close_file()
for exo in exo_list:
    exo.close()
if config.VARS_TO_PLOT:
    plotters.save_plot(filename=exo_list[0].filename.replace(
        '_LEFT.csv', '').replace('_RIGHT.csv', ''), vars_to_plot=config.VARS_TO_PLOT)

print('Done!!!')
