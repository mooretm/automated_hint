""" Settings variables for automated HINT. """

# Define dictionary items
fields = {
    # Session variables
    'subject': {'type': 'str', 'value': '999'},
    'condition': {'type': 'str', 'value': "test"},
    
    # Stimulus variables
    'randomize': {'type': 'int', 'value': 0},
    'repetitions': {'type': 'int', 'value': 1},
    'lists': {'type': 'str', 'value': '1, 2'},
    'import_audio_path': {'type': 'str', 'value': r'.\stimuli\audio'},
    'matrix_file_path': {'type': 'str', 'value': r'.\setup\matrix_HINT.csv'},
    'step_sizes': {'type': 'str', 'value': '4, 4, 4, 4, 2'},

    # Presentation level variables
    'adjusted_level_dB': {'type': 'float', 'value': -25.0},
    'desired_level_dB': {'type': 'float', 'value': 65},
    'noise_level_dB': {'type': 'float', 'value': 65},
    'starting_level_dB': {'type': 'float', 'value': 65},

    # Audio device variables
    'audio_device': {'type': 'int', 'value': 999},
    'channel_routing': {'type': 'str', 'value': '1'},

    # Calibration variables
    'cal_file': {'type': 'str', 'value': 'cal_stim.wav'},
    'cal_level_dB': {'type': 'float', 'value': -30.0},
    'slm_reading': {'type': 'float', 'value': 70.0},
    'slm_offset': {'type': 'float', 'value': 100.0},

    # Version control variables
    'config_file_status': {'type': 'int', 'value': 0},
    'check_for_updates': {'type': 'str', 'value': 'yes'},
    'version_lib_path': {'type': 'str', 'value': r'\\starfile\Public\Temp\MooreT\Personal Files\admin\versions.xlsx'},
}
