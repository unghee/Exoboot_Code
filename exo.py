import csv
import logging
import os
import sys
import time
import warnings
from dataclasses import dataclass

import numpy as np

import config_util
import constants
import custom_filters
from flexseapython import fxUtil, pyFlexsea


def connect_to_exo(port: str, baudRate: int, frequency: int, shouldLog=False):
    '''Args: 
        port: str from 'com.txt' in flexseapython/
        baudRate: int from 'com.txt' in flexseapython/
        shouldLog: bool indicating whether logging should be done with the flexsea lib.'''
    try:
        devId = pyFlexsea.fxOpen(port, baudRate, logLevel=6)
        pyFlexsea.fxStartStreaming(
            devId=devId, frequency=frequency, shouldLog=shouldLog)
        return devId
    except IOError:
        print('Unable to open exo on port: ', port,
              ' This is okay if only one exo is connected!')
        return None


class Exo():
    def __init__(self,
                 devId: int,
                 file_ID: str = None,
                 target_frequency: float = 200,
                 do_read_fsrs: bool = False):
        '''Exo object is the primary interface with the Dephy ankle exos.
        Args:
            devId: int. Unique integer to identify the exo in flexsea's library. Returned by connect_to_exo
            file_ID: str. Unique string added to filename. If None, no file will be saved.
            do_read_dsrs: bool indicating whether to read FSRs '''
        self.devId = devId
        self.file_ID = file_ID
        self.do_read_fsrs = do_read_fsrs
        if self.devId is None:
            print('Exo obj created but no exoboot connected. Some methods available')
        elif self.devId in constants.LEFT_EXO_DEV_IDS:
            self.side = constants.Side.LEFT
            self.motor_sign = -1
            self.ankle_to_motor_angle_polynomial = constants.LEFT_ANKLE_TO_MOTOR
            self.ankle_angle_offset = constants.LEFT_ANKLE_ANGLE_OFFSET
        elif self.devId in constants.RIGHT_EXO_DEV_IDS:
            self.side = constants.Side.RIGHT
            self.motor_sign = 1
            self.ankle_to_motor_angle_polynomial = constants.RIGHT_ANKLE_TO_MOTOR
            self.ankle_angle_offset = constants.RIGHT_ANKLE_ANGLE_OFFSET
        else:
            raise ValueError(
                'devId: ', self.devId, 'not found in LEFT_EXO_DEV_IDS or RIGHT_EXO_DEV_IDS')
        self.motor_offset = 0
        # ankle velocity filter is hardcoded for simplicity, but can be factored out if necessary
        self.ankle_velocity_filter = custom_filters.Butterworth(
            N=2, Wn=10, fs=target_frequency)
        if self.do_read_fsrs:
            try:
                if os.uname().nodename == 'raspberrypi':
                    import gpiozero
                    self.data = self.DataContainerWithFSRs()
                    if self.side == constants.Side.LEFT:
                        self.heel_fsr_detector = gpiozero.Button(
                            pin=constants.LEFT_HEEL_FSR_PIN)
                        self.toe_fsr_detector = gpiozero.Button(
                            pin=constants.LEFT_TOE_FSR_PIN)
                    else:
                        self.heel_fsr_detector = gpiozero.Button(
                            pin=constants.RIGHT_HEEL_FSR_PIN)
                        self.toe_fsr_detector = gpiozero.Button(
                            pin=constants.RIGHT_TOE_FSR_PIN)

            except:
                raise Exception('Can only use FSRs with rapberry pi!')
        else:
            self.data = self.DataContainer()

        self.has_calibrated = False
        self.is_clipping = False
        if self.file_ID is not None:
            self.setup_data_writer(file_ID=file_ID)
        if self.devId is not None:
            self.update_gains(Kp=constants.DEFAULT_KP,
                              Ki=constants.DEFAULT_KI,
                              Kd=constants.DEFAULT_KD,
                              K=0,
                              B=0,
                              ff=constants.DEFAULT_FF)
            self.motor_to_ankle_torque_polynomial = np.polyder(
                self.ankle_to_motor_angle_polynomial) * constants.ENC_CLICKS_TO_DEG

    @dataclass
    class DataContainer:
        '''A nested dataclass within Exo, reserving space for instantaneous data.'''
        state_time: float = 0
        loop_time: float = 0
        accel_x: float = 0
        accel_y: float = 0
        accel_z: float = 0
        gyro_x: float = 0
        gyro_y: float = 0
        gyro_z: float = 0
        motor_angle: int = 0
        motor_velocity: float = 0
        motor_current: int = 0
        ankle_angle: float = 0
        ankle_velocity: float = 0
        ankle_torque_from_current: float = 0
        did_heel_strike: bool = False
        gait_phase: float = 0
        did_toe_off: bool = False
        commanded_current: int = None
        commanded_position: int = None
        commanded_torque: float = None  # TODO(maxshep) remove
        slack: int = None

    @dataclass
    class DataContainerWithFSRs(DataContainer):
        heel_fsr: bool = True
        toe_fsr: bool = True

    def close(self):
        self.command_controller_off()
        time.sleep(0.05)
        pyFlexsea.fxStopStreaming(self.devId)
        time.sleep(0.2)
        pyFlexsea.fxClose(self.devId)
        self.close_file()
        if self.do_read_fsrs:
            self.heel_fsr_detector.close()
            self.toe_fsr_detector.close()

    def update_gains(self, Kp=None, Ki=None, Kd=None, K=None, B=None, ff=None):
        '''Optionally updates individual exo gain values, and sends to Actpack.'''
        if Kp is not None:
            self.Kp = Kp
        if Ki is not None:
            self.Ki = Ki
        if Kd is not None:
            self.Kd = Kd
        if K is not None:
            self.K = K
        if B is not None:
            self.B = B
        if ff is not None:
            self.ff = ff
        pyFlexsea.fxSetGains(self.devId, self.Kp, self.Ki,
                             self.Kd, self.K, self.B, self.ff)

    def read_data(self, do_print=False, loop_time=None):
        '''IMU data comes from Dephy in RHR, with positive XYZ pointing
        backwards, downwards, and rightwards on the right side and forwards,
        downwards, and leftwards on the left side. It is converted here
        to LHR on left side and RHR on right side. XYZ axes now point
        forwards, upwards, and outwards (laterally).'''
        if loop_time is not None:
            self.data.loop_time = loop_time
        last_ankle_angle = self.data.ankle_angle
        self.last_state_time = self.data.state_time
        actpack_data = pyFlexsea.fxReadDevice(self.devId)
        self.data.state_time = actpack_data.state_time * constants.MS_TO_SECONDS
        self.data.accel_x = -1 * self.motor_sign * \
            actpack_data.accelx * constants.ACCEL_GAIN
        self.data.accel_y = -1 * actpack_data.accely * constants.ACCEL_GAIN
        self.data.accel_z = actpack_data.accelz * constants.ACCEL_GAIN
        self.data.gyro_x = -1 * actpack_data.gyrox * constants.GYRO_GAIN
        self.data.gyro_y = -1 * self.motor_sign * \
            actpack_data.gyroy * constants.GYRO_GAIN
        self.data.gyro_z = self.motor_sign * actpack_data.gyroz * constants.GYRO_GAIN
        '''Motor angle and current are kept in Dephy's orientation, but ankle
        angle and torque are converted to positive = plantarflexion.'''
        self.data.motor_angle = actpack_data.mot_ang
        self.data.motor_velocity = actpack_data.mot_vel
        self.data.motor_current = actpack_data.mot_cur
        self.data.ankle_angle = (-1 * self.motor_sign * actpack_data.ank_ang *
                                 constants.ENC_CLICKS_TO_DEG + self.ankle_angle_offset)
        self.data.ankle_torque_from_current = self._motor_current_to_ankle_torque(
            self.data.motor_current)
        if self.has_calibrated:
            self.data.slack = self.get_slack()

        if (self.last_state_time is None or
            last_ankle_angle is None or
                self.data.state_time-self.last_state_time > 20):
            self.data.ankle_velocity = 0
        elif self.data.state_time == self.last_state_time:
            pass  # Keep old velocity
        else:
            angular_velocity = (
                self.data.ankle_angle - last_ankle_angle)/(self.data.state_time-self.last_state_time)
            self.data.ankle_velocity = self.ankle_velocity_filter.filter(
                angular_velocity)
        if self.do_read_fsrs:
            self.data.heel_fsr = self.heel_fsr_detector.value
            self.data.toe_fsr = self.toe_fsr_detector.value
        if do_print:
            fxUtil.clearTerminal()
            print('acc_x:                ', self.data.accel_x)
            print('acc_y:                ', self.data.accel_y)
            print('acc_z:                ', self.data.accel_z)
            print('gyro_x:               ', self.data.gyro_x)
            print('gyro_y:               ', self.data.gyro_y)
            print('gyro_z:               ', self.data.gyro_z)
            print('state_time:           ', self.data.state_time)
            print('motor_angle:          ', self.data.motor_angle)
            print('motor_velocity:       ', self.data.motor_velocity)
            print('motor_current:        ', self.data.motor_current)
            print('ankle_angle:          ', self.data.ankle_angle)

    def get_batt_voltage(self):
        actpack_data = pyFlexsea.fxReadDevice(self.devId)
        return actpack_data.batt_volt

    def setup_data_writer(self, file_ID: str):
        '''file_ID is used as a custom file identifier after date.'''
        if file_ID is not None:
            subfolder_name = 'exo_data/'
            filename = subfolder_name + \
                time.strftime("%Y%m%d_%H%M") + file_ID + \
                '_' + self.side.name + '.csv'
            self.my_file = open(filename, 'w', newline='')
            self.writer = csv.DictWriter(
                self.my_file, fieldnames=self.data.__dict__.keys())
            self.writer.writeheader()
            self._did_heel_strike_hold = False
            self._did_toe_off_hold = False

    def write_data(self, only_write_if_new: bool = True):
        '''Writes data file, optionally only if there is new actpack data.'''
        if self.file_ID is not None and only_write_if_new:
            # This logic is messy because is_heel_strike and is_toe_off are calculated more frequently,
            # So to write them we need to store if they occurred.
            if self.data.did_heel_strike:
                self._did_heel_strike_hold = True
            if self.data.did_toe_off:
                self._did_toe_off_hold = True
            if self.last_state_time != self.data.state_time:
                # Temporarily replace did_heel_strike and did_toe_off with holds
                current_did_heel_strike = self.data.did_heel_strike
                current_did_toe_off = self.data.did_toe_off
                self.data.did_heel_strike = self._did_heel_strike_hold
                self.data.did_toe_off = self._did_toe_off_hold
                self.writer.writerow(self.data.__dict__)
                # Reset to False (will fail if heel strikes / toe offs occur within ~10 ms of each other.)
                self.data.did_heel_strike = current_did_heel_strike
                self._did_heel_strike_hold = False
                self.data.did_toe_off = current_did_toe_off
                self._did_toe_off_hold = False
        else:
            if self.file_ID is not None:
                self.writer.writerow(self.data.__dict__)

    def close_file(self):
        if self.file_ID is not None:
            self.my_file.close()

    def command_current(self, desired_mA: int):
        '''Commands current (mA), with positive = PF on right, DF on left.'''
        if abs(desired_mA) > constants.MAX_ALLOWABLE_CURRENT_COMMAND:
            self.command_controller_off()
            raise ValueError(
                'abs(desired_mA) must be < constants.MAX_ALLOWABLE_CURRENT_COMMAND')
        pyFlexsea.fxSendMotorCommand(
            self.devId, pyFlexsea.FxCurrent, desired_mA)
        self.data.commanded_current = desired_mA
        self.data.commanded_position = None

    def command_voltage(self, desired_mV: int):
        '''Commands voltage (mV), with positive = PF on right, DF on left.'''
        if abs(desired_mV) > constants.MAX_ALLOWABLE_VOLTAGE_COMMAND:
            raise ValueError(
                'abs(desired_mV) must be < constants.MAX_ALLOWABLE_VOLTAGE_COMMAND')
        pyFlexsea.fxSendMotorCommand(
            self.devId, pyFlexsea.FxVoltage, desired_mV)
        self.data.commanded_current = None
        self.data.commanded_position = None

    def command_motor_angle(self, desired_motor_angle: int):
        '''Commands motor angle (counts). Pay attention to the sign!'''
        pyFlexsea.fxSendMotorCommand(
            self.devId, pyFlexsea.FxPosition, desired_motor_angle)
        self.data.commanded_current = None
        self.data.commanded_position = desired_motor_angle

    def command_motor_impedance(self, theta0: int, K: int, B: int):
        '''Commands motor impedance, with theta0 a motor position (int).'''
        # K and B are modified by updating gains (weird, yes)
        if K > constants.MAX_ALLOWABLE_K_COMMAND or K < 0:
            raise ValueError(
                'K must be positive, and less than max. tested K in constants.py')
        if B > constants.MAX_ALLOWABLE_B_COMMAND or B < 0:
            raise ValueError(
                'B must be positive, and less than max. tested B in constants.py')
        if self.K != K or self.B != B:
            # Only send gains when necessary
            self.update_gains(K=int(K), B=int(B))
        pyFlexsea.fxSendMotorCommand(
            self.devId, pyFlexsea.FxImpedance, int(theta0))
        self.data.commanded_current = None
        self.data.commanded_position = None

    def command_torque(self, desired_torque: float, do_return_command_torque=False):
        '''Applies desired torque (Nm) in plantarflexion only (positive torque)'''
        self.data.commanded_torque = desired_torque  # TODO(maxshep) remove
        if desired_torque < 0:
            print('desired_torque: ', desired_torque)
            raise ValueError('Cannot apply negative torques')
        max_allowable_torque = self.calculate_max_allowable_torque()
        if desired_torque > max_allowable_torque:
            if self.is_clipping is False:  # Only print once when clipping occurs before reset
                logging.warning('Torque was clipped!')
            desired_torque = max_allowable_torque
            self.is_clipping = True
        else:
            self.is_clipping = False
        desired_current = self._ankle_torque_to_motor_current(
            torque=desired_torque)
        self.command_current(desired_mA=desired_current)
        if do_return_command_torque:
            return desired_torque

    def command_ankle_angle(self, desired_ankle_angle):
        '''Controls ankle position (deg), assuming no slack'''
        raise ValueError('not tested!')
        if not self.has_calibrated:
            raise ValueError(
                'Must perform standing calibration before performing this task')
        if (desired_ankle_angle > constants.MAX_ANKLE_ANGLE or
                desired_ankle_angle < constants.MIN_ANKLE_ANGLE):
            raise ValueError(
                'Desired angle must within the range dictated in constants.py ')
        desired_motor_angle = self.ankle_angle_to_motor_angle(
            desired_ankle_angle)
        return desired_motor_angle
        # command position

    def command_ankle_impedance(self, theta0_ankle: float, K_ankle: float, B_ankle: float = 0):
        theta0_motor = self.ankle_angle_to_motor_angle(theta0_ankle)
        K_dephy = K_ankle / constants.DEPHY_K_TO_ANKLE_K
        # B_dephy = B_ankle / constants.DEPHY_B_TO_ANKLE_B
        self.command_motor_impedance(theta0=theta0_motor, K=K_dephy, B=0)

    def command_controller_off(self):
        pyFlexsea.fxSendMotorCommand(self.devId, pyFlexsea.FxNone, 0)

    def command_slack(self, desired_slack=10000):
        if not self.has_calibrated:
            raise ValueError(
                'Must perform standing calibration before performing this task')
        '''Commands position based on desired slack (motor counts)'''
        if desired_slack < 0:
            raise ValueError('Desired slack must be positive')
        # Desired motor angle requires estimating motor angle from ankle angle and adding/subtracting slack
        desired_motor_angle = int(
            -1 * self.motor_sign * desired_slack +
            self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        self.command_motor_angle(
            desired_motor_angle=desired_motor_angle)

    def get_slack(self):
        '''Returns slack in motor counts, with positive = actual slack.'''
        slack = -1*self.motor_sign*(self.data.motor_angle -
                                    self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        return slack

    def calculate_max_allowable_torque(self):
        max_allowable_torque = max(
            0, self._motor_current_to_ankle_torque(current=self.motor_sign*constants.MAX_ALLOWABLE_CURRENT_COMMAND))
        return max_allowable_torque

    def _motor_current_to_ankle_torque(self, current: int) -> float:
        '''Converts current (mA) to torque (Nm), based on side and transmission ratio (no dynamics)'''
        motor_torque = current*constants.MOTOR_CURRENT_TO_MOTOR_TORQUE
        ankle_torque = motor_torque * \
            np.polyval(self.motor_to_ankle_torque_polynomial,
                       self.data.ankle_angle)
        return ankle_torque

    def _ankle_torque_to_motor_current(self, torque: float) -> int:
        '''Converts torque (Nm) to current (mA), based on side and transmission ratio (no dynamics)'''
        motor_torque = torque / np.polyval(self.motor_to_ankle_torque_polynomial,
                                           self.data.ankle_angle)
        motor_current = int(
            motor_torque / constants.MOTOR_CURRENT_TO_MOTOR_TORQUE)
        return motor_current

    def ankle_angle_to_motor_angle(self, ankle_angle):
        '''Calculate equivalent motor position via polynomial evaluation.'''
        if not self.has_calibrated:
            raise ValueError(
                'Must perform standing calibration before performing this task')
        if ankle_angle > constants.MAX_ANKLE_ANGLE or ankle_angle < constants.MIN_ANKLE_ANGLE:
            print('ankle angle: ', ankle_angle)
            raise ValueError(
                'Attempted to convert ankle angle outside allowable bounds')
        motor_angle = int(np.polyval(
            self.ankle_to_motor_angle_polynomial, ankle_angle) + self.motor_offset)
        return motor_angle

    def standing_calibration(self,
                             calibration_mV: int = 1600,
                             max_seconds_to_calibrate: float = 5,
                             current_threshold: float = 1300,
                             require_user_input: bool = True):
        '''Brings up slack, calibrates ankle and motor offset angles.'''
        if require_user_input:
            input(['Press any key to calibrate exo on ' + str(self.side)])
            time.sleep(0.5)
        print('Calibrating...')
        current_filter = custom_filters.MovingAverage(window_size=10)
        self.command_voltage(desired_mV=self.motor_sign * calibration_mV)
        t0 = time.time()
        while time.time()-t0 < max_seconds_to_calibrate:
            time.sleep(0.01)
            self.read_data()
            if abs(current_filter.filter(self.data.motor_current)) > current_threshold:
                break
        else:
            # Enters here if while loop doesn't break
            self.command_controller_off()
            raise RuntimeError('Calibration Timed Out!!!')
        self.has_calibrated = True
        self.motor_offset = (self.data.motor_angle -
                             self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        for ramp_down_value in np.arange(1, 0, -0.01):
            time.sleep(0.01)
            self.command_voltage(desired_mV=ramp_down_value *
                                 self.motor_sign * calibration_mV)
        self.command_controller_off()
        print('Finished Calibrating ', self.side)

    def _test_units(self):
        # self.command_current(-2000)
        # self.update_gains(Kp=250, Ki=250, Kd=20, ff=100)
        for _ in range(1000):
            time.sleep(0.005)
            self.read_data()
            print(self.data.ankle_angle)
            # self.command_slack(desired_slack=5000)
            # print('slack', self.get_slack())
            self.write_data()

    def _chirp_test(self, peak_freq, duration, magnitude):
        t0 = time.time()
        t = 0
        while t < duration:
            self.read_data()
            time.sleep(0.01)
            t = time.time()-t0
            desired_torque = magnitude + magnitude * \
                np.sin(3.14*peak_freq/duration*t**2)
            self.command_torque(desired_torque=desired_torque)
            self.data.accel_x = desired_torque  # store here
            self.write_data()

    def _chirp_test_position(self, peak_freq, duration, magnitude_deg):
        # roughly equivalent to ankle excursion of magnitude_deg
        magnitude = magnitude_deg/0.0219 * 14
        t0 = time.time()
        t = 0

        self.read_data()
        starting_motor_angle = self.data.motor_angle

        while t < duration:
            self.read_data()
            time.sleep(0.01)
            t = time.time()-t0
            desired_angle = starting_motor_angle + magnitude * \
                np.sin(3.14*peak_freq/duration*t**2)
            self.command_motor_angle(desired_motor_angle=desired_angle)
            self.write_data()


if __name__ == '__main__':
    import util
    exo_list = []
    portList, baudRate = util.load_ports_and_baudrate_from_com()
    for port in portList:
        devId = connect_to_exo(port=port, baudRate=baudRate, frequency=100)
        if devId is not None:
            exo_list.append(Exo(devId=devId, file_ID='Test'))
    if not exo_list:  # (if empty)
        raise RuntimeError('No Exos connected')

    for exo in exo_list:
        # exo.standing_calibration()
        # exo.command_motor_impedance(theta0=exo.data.motor_angle, K=500, B=0)
        # time.sleep(5)
        # exo.command_controller_off()
        print(exo.get_batt_voltage())
        exo.close()
