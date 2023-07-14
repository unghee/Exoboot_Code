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
import numpy as np


#torque_profile = np.zeros(100)
"""[8.288293838500977, 7.41025972366333, 6.616360187530518, 5.946132183074951, 5.439113616943359, 5.101890563964844, 
5.2245354652404785, 5.757272243499756, 6.051341533660889, 6.692984104156494, 7.0892014503479, 7.113550662994385, 6.893687725067139, 
6.587777614593506, 6.441828727722168, 6.371031761169434, 6.650856971740723, 6.529520511627197, 6.324128150939941, 6.16853666305542, 
6.170462608337402, 6.544578552246094, 6.1557416915893555, 5.18583869934082, 4.360032558441162, 3.7516212463378906, 2.649479627609253, 
2.313070297241211, 2.9656550884246826, 4.53773832321167, 6.539644241333008, 7.445051193237305, 8.095815658569336, 9.471872329711914, 
7.275458812713623, 5.398955821990967, 4.238779067993164, 3.823606252670288, 3.944174289703369, 4.341067790985107, 5.743892192840576,
 7.426661968231201, 9.016322135925293, 7.285861968994141, 7.175071716308594, 7.154747486114502, 7.489355087280273, 7.804320812225342, 
 8.24379825592041, 9.058961868286133, 8.922183990478516, 8.806507110595703, 8.346049308776855, 8.138028144836426, 7.960187911987305,
  8.917771339416504, 8.093070030212402, 5.960103988647461, 2.8361170291900635, -0.9650033116340637, -4.54809045791626, -8.64715576171875, 
  -9.511663436889648, -7.740748405456543, -3.54040789604187, -0.3012145757675171, 2.6928675174713135, 5.359005928039551, 6.8848371505737305, 
  6.998980522155762, 5.680872917175293, 5.92738151550293, 5.7333197593688965, 5.684418201446533, 5.648083686828613, 5.666100978851318, 
  5.766464710235596, 5.650455951690674, 5.576498985290527, 5.605972766876221, 5.67177677154541, 5.678019046783447, 5.949980735778809, 
  6.067166805267334, 6.254060745239258, 6.255392074584961, 6.2189249992370605, 6.0487260818481445, 5.91334867477417, 5.913013935089111, 
  5.928750514984131, 5.880381107330322, 5.9197611808776855, 6.0590057373046875, 5.938861846923828, 5.936643600463867, 5.9314727783203125,
   5.921031951904297, 5.900171756744385, 5.863742351531982]"""

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
    #STANCE_CONTROL_STYLE: Type[StanceCtrlStyle] = StanceCtrlStyle.FOURPOINTSPLINE
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
    PEAK_TORQUE: float = 12

    """RISE_FRACTION: float = 0.376400032043457#0.2#0.075 
    PEAK_FRACTION: float = 0.59497730255127#0.53#0.33535#
    FALL_FRACTION: float = 0.65#0.60#0.44478#
    PEAK_TORQUE: float = 17.2818012237549#5#18.96235#"""
    SPLINE_BIAS: float = 3  # Nm

    #Varun Controller, Continuous torque
    torque_profile = np.zeros(100)
    action_received: float = False

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
    CONTROLLER_ALGORITHM_COMMUNICATION = f"{'141.212.77.28'}:" f"{'7075'}"
    ALGORITHM_CONTROLLER_COMMUNICATION = f"{'67.194.47.118'}:" f"{'5050'}"


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
