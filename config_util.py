from typing import Type, List
from dataclasses import dataclass, field
import time
import csv
import sys
import importlib
from enum import Enum
import argparse
import constants
import os

torque_profile = [3.85632354298339, 2.64928505734501, 2.19254340731786, 2.28149527844568, 2.71153735627224, 3.58850718454041, 3.25824047087135, 3.43341900105777, 3.69050035822393, 4.07959414878489, 4.12148534296455, 4.25368163433673, 4.56492780355551, 4.07473982858473, 3.61169937058633, 3.35983841084969, 3.58537215572969, 4.07842383025961, 4.28982938400937, 4.16755596330112, \
                               4.54452112483794, 4.97528488658277, 4.26676647385884, 3.37354633916844, 3.02360513972130, 2.30604165976297, 1.52984653757886, 1.74176930399100, 1.84712208167220, 2.50812984428615, \
                               3.43102495449063, 3.69737030571121, 3.93090459695928, 4.55913434503884, 4.89341255088155, 5.54977390098578, 7.50194588598617, 8.87749955603490, 10.8893479232789, 12.7225871096851, 14.4387800922395, 15.8960544410945, 15,15, \
                               15,15,15,15,15,15,15,15,15,15,15,15,15,15, 14.0646346601844, 12.1609553291797, 9.83059826573726, 7.91142262288924, 6.07230704504248, 4.38679944145677, 3.92107328398523, 3.16633476032315, \
                               2.71278365547210, 3.06612670245022, 3.42706402420999, 3.64127420037985, 3.38843749160322, 3.77379709879310, 3.42936029267312, 3.68347083567085, 3.56301529751718, 3.23965841001272, 3.33620180630685, 3.53508733310225, 2.82684737780086, 2.29435135946539, 2.71326237932198, 2.54793579358701, 2.90572420095746, 2.83516616134697, 2.70566658759981, \
                               3.00729027577632, 3.46519682872717, 3.44015213540198, 4.15663336917760, 4.57301863598826, 5.16118518233301, 5.09956033769251, 4.09395357875526, 3.65748224695027, 3.18025085067750, 2.95722707993278, 2.69626025111302, 2.79078869617124, 3.37127760348953, 4.56819216145001]

class Task(Enum):
    '''Used to determine gait_event_detector used and state machines used.'''
    WALKING = 0
    STANDINGPERTURBATION = 1
    BILATERALSTANDINGPERTURBATION = 2
    SLIPDETECTFROMSYNC = 3
    WALKINGMLGAITPHASE = 4


class StanceCtrlStyle(Enum):
    '''Used to determine behavior during stance.'''
    #FOURPOINTSPLINE = 0
    VARUN = 0
    GENERICSPLINE = 1
    SAWICKIWICKI = 2
    GENERICIMPEDANCE = 3
    FIVEPOINTSPLINE = 4
    FOURPOINTSPLINE = 5 #*


@dataclass
class ConfigurableConstants():
    '''Class that stores configuration-related constants.

    These variables serve to allow 1) loadable configurations from files in /custom_constants/, 
    2) online updating of device behavior via parameter_passers.py, and 3) to store calibration 
    details. Below are the default config constants. DO NOT MODIFY DEFAULTS. Write your own short
    script in /custom_constants/ (see default_config.py for example).
    (see )  '''
    # Set by functions... no need to change in config file
    loop_time: float = 0
    actual_time: float = time.time()
    LEFT_STANDING_ANGLE: float = None  # Deg
    RIGHT_STANDING_ANGLE: float = None  # Deg

    TARGET_FREQ: float = 175  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    DO_DEPHY_LOG: bool = False
    DEPHY_LOG_LEVEL: int = 4
    ONLY_LOG_IF_NEW: bool = True

    TASK: Type[Task] = Task.WALKING
    """STANCE_CONTROL_STYLE: Type[
        StanceCtrlStyle] = StanceCtrlStyle.FOURPOINTSPLINE"""
    STANCE_CONTROL_STYLE: Type[StanceCtrlStyle] = StanceCtrlStyle.VARUN
    MAX_ALLOWABLE_CURRENT = 20000  # mA

    # Gait State details
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05
    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.60
    REEL_IN_MV: int = 1200
    REEL_IN_SLACK_CUTOFF: int = 1200
    REEL_IN_TIMEOUT: float = 0.2
    NUM_STRIDES_REQUIRED: int = 2
    SWING_ONLY: bool = False

    # 4 point Spline
    #Original 
    """RISE_FRACTION: float = 0.2#0.075 
    PEAK_FRACTION: float = 0.53#0.33535#
    FALL_FRACTION: float = 0.60#0.44478#
    PEAK_TORQUE: float = 5#18.96235#"""

    RISE_FRACTION: float = 0.2#0.075 
    PEAK_FRACTION: float = 0.53#0.33535#
    FALL_FRACTION: float = 0.65#0.44478#
    PEAK_TORQUE: float = 8

    """RISE_FRACTION: float = 0.376400032043457#0.2#0.075 
    PEAK_FRACTION: float = 0.59497730255127#0.53#0.33535#
    FALL_FRACTION: float = 0.65#0.60#0.44478#
    PEAK_TORQUE: float = 17.2818012237549#5#18.96235#"""
    SPLINE_BIAS: float = 3  # Nm

    # Impedance
    K_VAL: int = 500
    B_VAL: int = 0
    B_RATIO: float = 0.5  # when B_VAL is a function of B_RATIO. 2.5 is approx. crit. damped
    SET_POINT: float = 0  # Deg

    READ_ONLY: bool = False  # Does not require Lipos
    DO_READ_FSRS: bool = False
    DO_READ_SYNC: bool = False

    PRINT_HS: bool = True  # Print heel strikes
    VARS_TO_PLOT: List = field(default_factory=lambda: [])
    DO_DETECT_SLIP: bool = False
    SLIP_DETECT_ACTIVE: bool = False
    DO_INCLUDE_GEN_VARS: bool = False
    SLIP_DETECT_DELAY: int = 0
    EXPERIMENTER_NOTES: str = 'Experimenter notes go here'

    #It is always zero untill the first generation
    #When this variable is non zero it means the update function can be called
    #It basically avoids any error caused by grpc call not being received due
    #to server not running on the optimizer side
    number_of_calls: int = 0
    generation: int = 0
    # DO NOT CHANGE THE DEFAULT VALUE
    confirmed: bool = False
    User_Ready = False

    #Needed for the Exosekeleton (EB 45, EB 51)
    resetting_time = 685  # the Exoboot typically stops updating after 731 seconds
    controller_stop_time = 710

    #Sending data using gRPC
    sending_ankle_velocity = []
    sending_ankle_angle = []

    #Receiving data from gRPC
    #torque_profile = []
    #ip addresses
    CONTROLLER_ALGORITHM_COMMUNICATION = f"{'141.212.77.28'}:" f"{'9090'}"
    ALGORITHM_CONTROLLER_COMMUNICATION = f"{'67.194.39.92'}:" f"{'5050'}"


class ConfigSaver():

    def __init__(self, file_ID: str, config: Type[ConfigurableConstants]):
        '''file_ID is used as a custom file identifier after date.'''
        self.file_ID = file_ID
        self.config = config
        subfolder_name = 'exo_data/'
        filename = subfolder_name + \
            time.strftime("%Y%m%d_%H%M_") + file_ID + \
            '_CONFIG' + '.csv'
        if os.path.exists(subfolder_name) and os.path.isdir(subfolder_name):
            pass
        else:
            os.mkdir(subfolder_name)
        self.my_file = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(self.my_file,
                                     fieldnames=self.config.__dict__.keys())
        self.writer.writeheader()

    def write_data(self, loop_time):
        '''Writes new row of Config data to Config file.'''
        self.config.loop_time = loop_time
        self.config.actual_time = time.time()
        self.writer.writerow(self.config.__dict__)

    def close_file(self):
        if self.file_ID is not None:
            self.my_file.close()


def load_config(config_filename) -> Type[ConfigurableConstants]:
    try:
        # strip extra parts off
        config_filename = config_filename.lower()
        if config_filename.endswith('_config'):
            config_filename = config_filename[:-7]
        elif config_filename.endswith('_config.py'):
            config_filename = config_filename[:-11]
        elif config_filename.endswith('.py'):
            config_filename = config_filename[:-4]
        config_filename = config_filename + '_config'
        module = importlib.import_module('.' + config_filename,
                                         package='custom_configs')
    except:
        error_str = 'Unable to find config file: ' + \
            config_filename + ' in custom_constants'
        raise ValueError(error_str)
    config = module.config
    print('Using ConfigurableConstants from: ', config_filename)
    return config


def parse_args():
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='Exoboot Code',
                                        description='Run Exoboot Controllers',
                                        epilog='Enjoy the program! :)')
    # Add the arguments
    my_parser.add_argument('-c',
                           '--config',
                           action='store',
                           type=str,
                           required=False,
                           default='default_config')
    # Execute the parse_args() method
    args = my_parser.parse_args()
    return args


def load_config_from_args():
    args = parse_args()
    config = load_config(config_filename=args.config)
    return config


def get_sync_detector(config: Type[ConfigurableConstants]):
    if config.DO_READ_SYNC:
        print('Creating sync detector')
        import gpiozero  # pylint: disable=import-error
        sync_detector = gpiozero.InputDevice(pin=constants.SYNC_PIN,
                                             pull_up=False)
        return sync_detector
    else:
        return None
