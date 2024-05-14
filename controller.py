""" Automated HINT. 

    Presents and scores the HINT. Audio files and sentence
    lists are baked in, resulting in a single EXE file. Trial
    data are written to CSV. 

    Written by: Travis M. Moore
    Created: May 08, 2024
"""

###########
# Imports #
###########
# Standard library
import datetime
import json
import logging.config
import logging.handlers
import os
import sys
import tkinter as tk
import time
import webbrowser
from pathlib import Path
from tkinter import messagebox

# Third party
import markdown
import numpy as np

# Custom
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')
import app_assets
import menus
import models
import setup
import tmpy
import views
from tmpy import tkgui
from tmpy import readwrite

##########
# Logger #
##########
logger = logging.getLogger(__name__)

def setup_logging(NAME):
    """ Create output log file path. 
        Import and update logging config JSON file.
        Apply config to logger.
    """
    # Create logging output file path based on app name
    flat_name = tmpy.functions.helper_funcs.flatten_text(NAME)
    _app_with_ext = flat_name + '.log.jsonl'
    filename = os.path.join(Path.home(), flat_name, _app_with_ext)

    # Specify logging config file path
    try:
        config_file = os.path.join(
            os.environ['TMPY'],
            'tmpy',
            'logger',
            'logger_config.json'
        )
    except KeyError:
        config_file = tmpy.logger.LOGGER_CONFIG_JSON

    # Import and update logging config file
    with open(config_file) as f_in:
        config = json.load(f_in)
        # Update output file location based on app name
        config['handlers']['file']['filename'] = filename
        # Pass in custom JSONFormatter
        config['formatters']['json']['()'] = tmpy.logger.JSONFormatter

    # Apply logging config
    logging.config.dictConfig(config)

#################
# Splash Screen #
#################
class Splash(tk.Toplevel):
    def __init__(self, parent, text):
        tk.Toplevel.__init__(self, parent)
        #logger.debug("Initializing splash screen")
        self.withdraw()
        self.title("Please wait")
        self.geometry("300x200")
        self.resizable(False, False)
        tk.Label(self, text=text).pack()
        self.center_splashscreen()
        self.update()
        

    def center_splashscreen(self):
        """ Center the splash screen. """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        print(f"\n\nscreen width, height: {screen_width}, {screen_height}")
        print(f"geometry: {self.geometry()}")
        self.deiconify()

###############
# Application #
###############
class Application(tk.Tk):
    """ Application root window. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #splash_screen = Splash(parent=self, text="Loading Automated HINT")

        self.withdraw() # Hide root window during setup

        #############
        # Constants #
        #############
        self.NAME = 'Automated HINT'
        self.VERSION = '0.1.0'
        self.EDITED = 'May 14, 2024'

        ################
        # Window setup #
        ################
        self.resizable(False, False)
        self.title(self.NAME)
        self.taskbar_icon = tk.PhotoImage(
            file=tkgui.shared_assets.images.LOGO_FULL_PNG
            )
        self.iconphoto(True, self.taskbar_icon)

        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Load current settings from file
        # or load defaults if file does not exist yet
        self.settings_model = tkgui.models.SettingsModel(
            parent=self,
            settings_vars=setup.settings_vars.fields,
            app_name=self.NAME
            )
        self._load_settings()

        # Set up custom logger as soon as config dir is created
        # (i.e., after settings model has been initialized)
        setup_logging(self.NAME)
        logger.debug("Started custom logger")
        logger.debug("Initializing application")

        # Default public attributes
        self.level_data = []
        logger.debug("Setting controller 'start' flag to True")
        self.start_flag = True

        # Assign special quit function on window close
        self.protocol('WM_DELETE_WINDOW', self._quit)

        # Load calibration model
        self.calibration_model = tkgui.models.CalibrationModel(self.settings)

        # Load main view
        self.main_view = views.MainView(self, self.settings)
        self.main_view.grid(row=5, column=5)

        # Create menu settings dictionary
        self._app_info = {
            'name': self.NAME,
            'version': self.VERSION,
            'last_edited': self.EDITED
        }
        # Load menus
        self.menu = menus.MainMenu(self, self._app_info)
        self.config(menu=self.menu)

        # Create data handler
        self.dh = tmpy.handlers.DataHandler()

        # Create score model
        self.sm = models.ScoreModel()

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileSettings>>': lambda _: self._show_settings_view(),
            '<<FileStart>>': lambda _: self.on_start(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsAudioSettings>>': lambda _: self._show_audio_dialog(),
            '<<ToolsCalibration>>': lambda _: self._show_calibration_dialog(),

            # Help menu
            '<<HelpREADME>>': lambda _: self._show_help(),
            '<<HelpChangelog>>': lambda _: self._show_changelog(),

            # Settings window
            '<<SettingsSubmit>>': lambda _: self._save_settings(),

            # Calibration window
            '<<CalPlay>>': lambda _: self.play_calibration_file(),
            '<<CalStop>>': lambda _: self.stop_audio(),
            '<<CalibrationSubmit>>': lambda _: self._calc_offset(),

            # Audio settings window
            '<<AudioViewSubmit>>': lambda _: self._save_settings(),

            # Main View
            '<<MainNext>>': lambda _: self.on_next(),
            '<<MainRepeat>>': lambda _: self.play(),
        }

        # Bind callbacks to sequences
        logger.debug("Binding callbacks to controller")
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        ###################
        # Version Control #
        ###################
        # Check for updates
        if self.settings['check_for_updates'].get() == 'yes':
            _filepath = self.settings['version_lib_path'].get()
            u = tkgui.models.VersionModel(_filepath, self.NAME, self.VERSION)
            if u.status == 'mandatory':
                logger.critical("This version: %s", self.VERSION)
                logger.critical("Mandatory update version: %s", u.new_version)
                messagebox.showerror(
                    title="New Version Available",
                    message="A mandatory update is available. Please install " +
                        f"version {u.new_version} to continue.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
                logger.critical("Application failed to initialize")
                self.destroy()
                return
            elif u.status == 'optional':
                messagebox.showwarning(
                    title="New Version Available",
                    message="An update is available.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
            elif u.status == 'current':
                pass
            elif u.status == 'app_not_found':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="Cannot retrieve version number!",
                    detail=f"'{self.NAME}' does not exist in the version library."
                 )
            elif u.status == 'library_inaccessible':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="The version library is unreachable!",
                    detail="Please check that you have access to Starfile."
                )

        # Destroy splash screen
        #splash_screen.destroy()

        # Temporarily disable Help menu until documents are written
        self.menu.help_menu.entryconfig('README...', state='disabled')

        # Center main window
        self.center_window()
        #self.center_window(self)

        # Initialization successful
        logger.info('Application initialized successfully')

    #####################
    # General Functions #
    #####################
    def center_window(self):
        """ Center the root window. """
        self.update_idletasks()
        logger.debug("Centering root window after drawing widgets")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        #print(f"\n\nscreen width, height: {screen_width}, {screen_height}")
        print(f"geometry: {self.geometry()}")
        self.deiconify()


    # def center_window2(self, window):
    #     """ Center the root window. """
    #     logger.debug("Centering root window after drawing widgets")
    #     window.update_idletasks()
    #     screen_width = window.winfo_screenwidth()
    #     screen_height = window.winfo_screenheight()
    #     size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    #     x = screen_width/2 - size[0]/2
    #     y = screen_height/2 - size[1]/2
    #     window.geometry("+%d+%d" % (x, y))
    #     window.deiconify()


    def _create_filename(self):
        """ Create file name and path. """
        logger.debug("Creating file name with date stamp")
        datestamp = datetime.datetime.now().strftime("%Y_%b_%d_%H%M")
        sub = self.settings['subject'].get()
        cond = self.settings['condition'].get()
        filename = '_'.join([sub, cond, datestamp, ".csv"])
        return filename


    def _quit(self):
        """ Exit the application. """
        logger.info("User ended the session")
        self.destroy()

    ###################
    # File Menu Funcs #
    ###################
    def _show_settings_view(self):
        """ Show session parameter dialog. """
        logger.debug("Calling settings view")
        views.SettingsView(self, self.settings)


    def _prepare_trials(self):
        """ Import matrix file and organize trials. """
        # Create MatrixHandler
        self.mh = tmpy.handlers.MatrixHandler(
            filepath=self.settings['matrix_file_path'].get(),
            randomize=self.settings['randomize'].get(),
            repetitions=self.settings['repetitions'].get()
        )
        
        # Convert string of HINT list numbers to list
        lists = tmpy.functions.helper_funcs.string_to_list(
            string_list=self.settings['lists'].get(),
            datatype='int'
            )
        
        # Grab specified lists
        mask = self.mh.matrix['list_num'].isin(lists)
        trials_df = self.mh.matrix[mask]

        return trials_df


    def on_start(self):
        """ Import matrix file and create TrialHandler. """
        logger.debug("Start button pressed")

        # Create filename with time stamp
        self.filename = self._create_filename()

        # Prepare trials
        trials = self._prepare_trials()

        # Format step sizes
        steps = tmpy.functions.helper_funcs.string_to_list(
            string_list=self.settings['step_sizes'].get(),
            datatype='int'
            )

        # Create adaptive trial handler
        self.ath = tmpy.handlers.AdaptiveTrialHandler(
            trials_df=trials,
            parameter=self.settings['starting_level_dB'].get(),
            step_sizes=steps
            )

        # Disable "Start" from File menu
        self.menu.file_menu.entryconfig('Start', state='disabled')

        # Enable user controls
        self.main_view.enable_user_controls(text="Next")

        # Start first trial
        self.on_next()

    #######################
    # Main View Functions #
    #######################
    def _prepare_stimulus(self):
        """ Prepare audio for playback. """
        logger.debug("Preparing audio for playback")

        # Calculate level based on SLM offset
        #self._calc_level(self.settings['desired_level_dB'].get())
        self._calc_level(self.ath.parameter)

        # Add directory to file name
        stim = Path(os.path.join(
            self.settings['import_audio_path'].get(),
            self.ath.trial_info['file']
            )
            )
        
        return stim


    def play(self):
        """ Begin audio playback. """
        # Prepare audio for playback
        stim = self._prepare_stimulus()
        
        # Present WGN
        self.present_audio(
            audio=stim,
            pres_level=self.settings['adjusted_level_dB'].get()
            )
        

    def _end_of_task(self):
        """ Present message to user and destroy root. """
        # Calculate the final SNR outcome of the HINT
        self.sm.get_snr(
            trial_levels=self.level_data, 
            noise_level=self.settings['noise_level_dB'].get()
            )

        messagebox.showinfo(
            title="Task Complete",
            message="You have completed the task!",
            detail=f"HINT score: {self.sm.final_snr} dB SNR"
        )
        logger.debug("Closing application")
        self.quit()


    def _save(self, responses):
        """ Save data to CSV, on a per trial basis, 
            after scoring each trial. 
        """
        # Add directory to filename
        directory = 'Data'
        fullpath = os.path.join(directory, self.filename)

        # Define items to include in CSV
        order = ['trial',
                 'subject', 
                 'condition', 
                 'list_num',
                 'sentence_num',
                 'desired_level_dB',
                 'correct',
                 'incorrect',
                 'step_size',
                 'response'
                 ]

        try:
            self.dh.save_data(
                filepath=fullpath,
                dict_list=[self.settings, responses, self.ath.trial_info],
                order=order
            )
        except PermissionError as e:
            logger.exception(e)
            messagebox.showerror(
                title="Access Denied",
                message="Data not saved! Cannot write to file!",
                detail=e
            )
            return
        except OSError as e:
            logger.exception(e)
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find file or directory!",
                detail=e
            )
            return
        

    def on_next(self):
        """ Get and present next trial. """
        logger.debug("Fetching next trial")

        # Score and save responses
        if not self.start_flag:
            # Score response
            scored_words = self.sm.score(
                words=self.main_view.words_dict,
                button_states=self.main_view.buttonstates_dict
            )

            # Write response to CSV
            self._save(scored_words)

            # Append trial level to level_data
            self.level_data.append(self.settings['desired_level_dB'].get())
        
        if self.start_flag:
            # Set start flag to False after intitial trial
            logger.debug("Setting 'start' flag to False")
            self.start_flag = False

        # Get next trial
        try:
            self.ath.next(response=self.sm.outcome)
        except IndexError:
            logger.warning("End of trials!")
            self._end_of_task()
            return
        
        # Display sentence with checkbuttons
        self.main_view.update_main_label(
            sentence=self.ath.trial_info['sentence'])

        # Update trial label
        self.main_view.update_trial_number(self.ath.trial_num)

        # Disable user controls during playback
        self.main_view.disable_user_controls(text="Presenting")

        # Present audio
        self.play()

        # Enable user controls after playback
        self.after(int(np.ceil(self.a.dur*1000)), 
                   lambda: self.main_view.enable_user_controls(text="Next")
                   )

    ###########################
    # Settings View Functions #
    ###########################
    def _load_settings(self):
        """ Load parameters into self.settings dict. """
        # Variable types
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create runtime dict from settingsmodel fields
        self.settings = dict()
        for key, data in self.settings_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])
        logger.debug("Loaded settings model fields into " +
            "running settings dict")


    def _save_settings(self, *_):
        """ Save current runtime parameters to file. """
        logger.debug("Calling settings model set and save funcs")
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
            self.settings_model.save()

    ########################
    # Tools Menu Functions #
    ########################
    def _show_audio_dialog(self):
        """ Show audio settings dialog. """
        logger.debug("Calling audio device window")
        tkgui.views.AudioView(self, self.settings)


    def _show_calibration_dialog(self):
        """ Display the calibration dialog window. """
        logger.debug("Calling calibration window")
        tkgui.views.CalibrationView(self, self.settings)

    ################################
    # Calibration Dialog Functions #
    ################################
    def play_calibration_file(self):
        """ Load calibration file and present. """
        logger.debug("Play calibration file called")
        # Get calibration file
        try:
            self.calibration_model.get_cal_file()
        except AttributeError:
            logger.exception("Cannot find internal calibration file!")
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find internal calibration file!",
                detail="Please use a custom calibration file."
            )
        # Present calibration signal
        self.present_audio(
            audio=Path(self.calibration_model.cal_file), 
            pres_level=self.settings['cal_level_dB'].get()
        )


    def _calc_offset(self):
        """ Calculate offset based on SLM reading. """
        # Calculate new presentation level
        self.calibration_model.calc_offset()
        # Save level - this must be called here!
        self._save_settings()


    def _calc_level(self, desired_spl):
        """ Calculate new dB FS level using slm_offset. """
        # Calculate new presentation level
        self.calibration_model.calc_level(desired_spl)
        # Save level - this must be called here!
        self._save_settings()

    #######################
    # Help Menu Functions #
    #######################
    def _show_help(self):
        """ Create html help file and display in default browser. """
        logger.debug("Calling README file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.README.README_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.README.README_HTML, 'w') as f:
            f.write(html)

        # Open README in default web browser
        webbrowser.open(app_assets.README.README_HTML)


    def _show_changelog(self):
        """ Create html CHANGELOG file and display in default browser. """
        logger.debug("Calling CHANGELOG file (will open in browser)")
        # Read markdown file and convert to html
        with open(app_assets.CHANGELOG.CHANGELOG_MD, 'r') as f:
            text = f.read()
            html = markdown.markdown(text)

        # Create html file for display
        with open(app_assets.CHANGELOG.CHANGELOG_HTML, 'w') as f:
            f.write(html)

        # Open CHANGELOG in default web browser
        webbrowser.open(app_assets.CHANGELOG.CHANGELOG_HTML)

    ###################
    # Audio Functions #
    ###################
    def _create_audio_object(self, audio, **kwargs):
        # Create audio object
        try:
            self.a = tmpy.audio_handlers.AudioPlayer(
                audio=audio,
                **kwargs
            )
        except FileNotFoundError:
            logger.exception("Cannot find audio file!")
            messagebox.showerror(
                title="File Not Found",
                message="Cannot find the audio file!",
                detail="Go to File>Session to specify a valid audio path."
            )
            self._show_settings_view()
            return
        except tmpy.audio_handlers.InvalidAudioType:
            raise
        except tmpy.audio_handlers.MissingSamplingRate:
            raise


    def _format_routing(self, routing):
        """ Convert space-separated string to list of ints
            for speaker routing.
        """
        logger.debug("Formatting channel routing string as list")
        routing = routing.split()
        routing = [int(x) for x in routing]
        return routing
    

    def _play(self, pres_level):
        """ Format channel routing, present audio and catch exceptions. """
        # Attempt to present audio
        try:
            self.a.play(
                level=pres_level,
                device_id=self.settings['audio_device'].get(),
                routing=self._format_routing(
                    self.settings['channel_routing'].get())
            )
        except tmpy.audio_handlers.InvalidAudioDevice as e:
            logger.error("Invalid audio device: %s", e)
            messagebox.showerror(
                title="Invalid Device",
                message="Invalid audio device! Go to Tools>Audio Settings " +
                    "to select a valid audio device.",
                detail = e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.InvalidRouting as e:
            logger.error("Invalid routing: %s", e)
            messagebox.showerror(
                title="Invalid Routing",
                message="Speaker routing must correspond with the " +
                    "number of channels in the audio file! Go to " +
                    "Tools>Audio Settings to update the routing.",
                detail=e
            )
            # Open Audio Settings window
            self._show_audio_dialog()
        except tmpy.audio_handlers.Clipping:
            logger.error("Clipping has occurred - aborting!")
            messagebox.showerror(
                title="Clipping",
                message="The level is too high and caused clipping.",
                detail="The waveform will be plotted when this message is " +
                    "closed for visual inspection."
            )
            self.a.plot_waveform("Clipped Waveform")


    def present_audio(self, audio, pres_level, **kwargs):
        # Load audio
        try:
            self._create_audio_object(audio, **kwargs)
        except tmpy.audio_handlers.InvalidAudioType as e:
            logger.error("Invalid audio format: %s", e)
            messagebox.showerror(
                title="Invalid Audio Type",
                message="The audio type is invalid!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return
        except tmpy.audio_handlers.MissingSamplingRate as e:
            logger.error("Missing sampling rate: %s", e)
            messagebox.showerror(
                title="Missing Sampling Rate",
                message="No sampling rate was provided!",
                detail=f"{e} Please provide a Path or ndarray object."
            )
            return

        # Play audio
        self._play(pres_level)


    def stop_audio(self):
        """ Stop audio playback. """
        logger.debug("User stopped audio playback")
        try:
            self.a.stop()
        except AttributeError:
            logger.debug("Stop called, but there is no audio object!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
