
import config_util
config = config_util.ConfigurableConstants()

config.TASK = config_util.Task.WALKINGMLGAITPHASE
config.READ_ONLY = False
peak_fraction_from_training = 0.63
config.RISE_FRACTION = 0.2*(1/peak_fraction_from_training)
config.PEAK_FRACTION = 0.53*(1/peak_fraction_from_training)
config.FALL_FRACTION = 1
config.PEAK_TORQUE = 5
config.SPLINE_BIAS = 3  # Nm
config.DO_READ_FSRS = True
config.VARS_TO_PLOT = ['heel_fsr', 'toe_fsr']
config.SWING_ONLY = True
config.DO_INCLUDE_GEN_VARS = True


''' Here are the variables that are updatable in config, and their defaults:

    TARGET_FREQ: float = 200  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    DO_DEPHY_LOG: bool = True
    DEPHY_LOG_LEVEL: int = 4
    TASK: Type[Task] = Task.WALKING
    STANCE_CONTROL_STYLE: Type[StanceCtrlStyle] = StanceCtrlStyle.FOURPOINTSPLINE
    MAX_ALLOWABLE_CURRENT = 20000  # mA

    # Gait State details
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05
    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62
    REEL_IN_TIMEOUT: float = 0.2

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5
    SPLINE_BIAS: float = 3  # Nm

    # Impedance
    K_VAL: int = 500
    B_VAL: int = 0
    SET_POINT: float = 0  # Deg

    READ_ONLY = False  # Does not require Lipos
    DO_READ_FSRS = False

    PRINT_HS = True  # Print heel strikes
    SLIP_DETECT_ACTIVE = False
'''
