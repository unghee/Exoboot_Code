from typing import Type
import config_util
import state_machines
import gait_state_estimators
import exoboot
import filters
import controllers


def get_gait_state_estimator(exo: exoboot.Exo,
                             config: Type[config_util.ConfigurableConstants]):
    '''Uses info from the config option to build a gait_state_estimator for a single exo.
    Refactored out of main_loop for readability.'''
    if config.TASK == config_util.Task.WALKING:
        heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
            height=config.HS_GYRO_THRESHOLD,
            gyro_filter=filters.Butterworth(N=config.HS_GYRO_FILTER_N,
                                            Wn=config.HS_GYRO_FILTER_WN,
                                            fs=config.TARGET_FREQ),
            delay=config.HS_GYRO_DELAY)
        gait_phase_estimator = gait_state_estimators.StrideAverageGaitPhaseEstimator()
        toe_off_detector = gait_state_estimators.GaitPhaseBasedToeOffDetector(
            fraction_of_gait=config.TOE_OFF_FRACTION)
        gait_state_estimator = gait_state_estimators.GaitStateEstimator(
            side=exo.side,
            data_container=exo.data,
            heel_strike_detector=heel_strike_detector,
            gait_phase_estimator=gait_phase_estimator,
            toe_off_detector=toe_off_detector,
            do_print_heel_strikes=config.PRINT_HS)

    elif config.TASK == config_util.Task.STANDINGPERTURBATION:
        gait_state_estimator = gait_state_estimators.SlipDetectorAP(
            data_container=exo.data)  # acc_threshold_x=0.35, time_out=5, max_acc_y=0.25, max_acc_z=0.25

    else:
        raise ValueError('Unknown TASK for get_gait_state_estimator')

    return gait_state_estimator


def get_state_machine(exo: exoboot.Exo,
                      config: Type[config_util.ConfigurableConstants]):
    '''Uses info from the config option to build a state_machine for a single exo.
    Refactored out of main_loop for readability.'''
    if config.TASK == config_util.Task.WALKING:
        reel_in_controller = controllers.SmoothReelInController(
            exo=exo, time_out=config.REEL_IN_TIMEOUT)
        swing_controller = controllers.StalkController(
            exo=exo, desired_slack=config.SWING_SLACK)
        reel_out_controller = controllers.SoftReelOutController(
            exo=exo, desired_slack=config.SWING_SLACK)
        if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
            stance_controller = controllers.FourPointSplineController(
                exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                peak_fraction=config.PEAK_FRACTION,
                fall_fraction=config.FALL_FRACTION,
                bias_torque=config.SPLINE_BIAS)
        elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle().SAWICKIWICKI:
            stance_controller = controllers.SawickiWickiController(
                exo=exo, k_val=config.K_VAL)
        state_machine = state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                            stance_controller=stance_controller,
                                                                            swing_controller=swing_controller,
                                                                            reel_in_controller=reel_in_controller,
                                                                            reel_out_controller=reel_out_controller)

    elif config.TASK == config_util.Task.STANDINGPERTURBATION:
        standing_controller = controllers.GenericImpedanceController(
            exo=exo, setpoint=10, k_val=100)
        if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.GENERICIMPEDANCE:
            slip_controller = controllers.GenericImpedanceController(
                exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
            slip_recovery_time = 1.01  # TODO(maxshep)
        elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
            print("using a spline based controller!")
            slip_controller = controllers.FourPointSplineController(
                exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                peak_fraction=config.PEAK_FRACTION,
                fall_fraction=config.FALL_FRACTION,
                bias_torque=config.SPLINE_BIAS,
                use_gait_phase=False)
            # slip_recovery_time = config.FALL_FRACTION-0.01
            slip_recovery_time = 0.99

        state_machine = state_machines.StandingPerturbationResponse(exo=exo,
                                                                    standing_controller=standing_controller,
                                                                    slip_controller=slip_controller,
                                                                    slip_recovery_time=slip_recovery_time)
    else:
        raise ValueError(
            'Unknown TASK or STANCE_CONTROL_STYLE for get_state_machine')

    return state_machine
