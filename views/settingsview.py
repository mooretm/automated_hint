""" Settings view for automated HINT. 

    Written by: Travis M. Moore
    Last edited: May 28, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from idlelib.tooltip import Hovertip
from tkinter import ttk

###########
# Logging #
###########
# Create new logger
logger = logging.getLogger(__name__)

################
# SettingsView #
################
class SettingsView(tk.Toplevel):
    """ View for setting session parameters. """
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        logger.debug("Initializing SettingsView")

        # Assign attributes
        self.parent = parent
        self.settings = settings

        # Window setup
        self.withdraw()
        self.resizable(False, False)
        self.title("Settings")
        self.grab_set()

        # Populate view with widgets
        self._draw_widgets()


    def _draw_widgets(self):
        """ Populate the MainView with widgets. """
        logger.debug("Drawing MainView widgets")

        ##########
        # Frames #
        ##########
        # Tooltip delay (ms)
        tt_delay = 1000

        # Shared frame settings
        frame_options = {'padx': 10, 'pady': 10, 'ipadx': 5, 'ipady': 5}
        widget_options = {'padx': 5, 'pady': (10, 0)}

        # Session info
        frm_session = ttk.Labelframe(self, text='Settings')
        frm_session.grid(row=5, column=5, **frame_options, sticky='nsew')

        # Sentence options
        frm_sentence = ttk.Labelframe(self, text='Sentence Options')
        frm_sentence.grid(row=10, column=5, **frame_options, sticky='nsew')

        # Noise options
        frm_noise = ttk.Labelframe(self, text='Noise Options')
        frm_noise.grid(row=15, column=5, **frame_options, sticky='nsew')

        ###########
        # Widgets #
        ###########
        # Subject
        lbl_sub = ttk.Label(frm_session, text="Subject:")
        lbl_sub.grid(row=5, column=5, sticky='e', **widget_options)
        sub_tt = Hovertip(
            anchor_widget=lbl_sub,
            text="A unique subject identifier."+
                "\nCan be alpha, numeric, or both.",
            hover_delay=tt_delay
            )
        ttk.Entry(frm_session, 
            textvariable=self.settings['subject']
            ).grid(row=5, column=10, sticky='w', **widget_options)

        # Condition
        lbl_condition = ttk.Label(frm_session, text="Condition:")
        lbl_condition.grid(row=10, column=5, sticky='e', **widget_options)
        condition_tt = Hovertip(
            anchor_widget=lbl_condition,
            text="A unique condition name.\nCan be alpha, numeric, or both." +
                "\nSeparate words with underscores.",
            hover_delay=tt_delay
            )
        ttk.Entry(frm_session, 
            textvariable=self.settings['condition']
            ).grid(row=10, column=10, sticky='w', **widget_options)
        
        # Lists
        lbl_lists = ttk.Label(frm_sentence,
                  text="List(s):",
                  takefocus=0
                  )
        lbl_lists.grid(row=5,
                         column=5,
                         sticky='e',
                         **widget_options
                         )
        lists_tt = Hovertip(
            anchor_widget=lbl_lists,
            text="The list numbers to include in the session." +
                "\nSeparate multiple values with a comma and space: 1, 2, 3",
            hover_delay=tt_delay
            )
        ttk.Entry(frm_sentence,
                  textvariable=self.settings['lists']
                  ).grid(row=5, column=10, **widget_options)
        
        # Sentence level
        lbl_sentence_level = ttk.Label(frm_sentence, text="Starting Level:")
        lbl_sentence_level.grid(row=10, 
                                column=5, 
                                sticky='e', 
                                **widget_options
                                )
        sentence_level_tt = Hovertip(
            anchor_widget=lbl_sentence_level,
            text="A single starting presentation level for the sentences.",
            hover_delay=tt_delay
            )
        ttk.Entry(frm_sentence, width=7,
            #textvariable=self.settings['desired_level_dB']
            textvariable=self.settings['starting_level_dB']
            ).grid(row=10, column=10, sticky='w', **widget_options)

        # Noise level
        lbl_noise_level = ttk.Label(frm_noise, text="Level:")
        lbl_noise_level.grid(row=5, column=5, sticky='e', **widget_options)
        noise_level_tt = Hovertip(
            anchor_widget=lbl_noise_level,
            text="A single presentation level for the noise.",
            hover_delay=tt_delay
            )
        ttk.Entry(frm_noise, width=7,
            textvariable=self.settings['noise_level_dB']
            ).grid(row=5, column=10, sticky='w', **widget_options)

        # Submit button
        btn_submit = ttk.Button(self, text="Submit", command=self._on_submit)
        btn_submit.grid(row=40, column=5, columnspan=2, pady=(0, 10))

        # Center the session dialog window
        self._center_window()


    #############
    # Functions #
    #############
    def _center_window(self):
        """ Center the TopLevel window over the root window. """
        logger.debug("Centering window over parent")
        # Get updated window size (after drawing widgets)
        self.update_idletasks()

        # Calculate the x and y coordinates to center the window
        x = self.parent.winfo_x() \
            + (self.parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = self.parent.winfo_y() \
            + (self.parent.winfo_height() - self.winfo_reqheight()) // 2
        
        # Set the window position
        self.geometry("+%d+%d" % (x, y))

        # Display window
        self.deiconify()


    def _on_submit(self):
        """ Send submit event to controller and close window. """
        logger.debug("Sending 'SUBMIT' event to controller")
        self.parent.event_generate('<<SettingsSubmit>>')
        logger.debug("Destroying SettingsView instance")
        self.destroy()


if __name__ == "__main__":
    pass
