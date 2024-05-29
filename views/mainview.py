""" Main view for automated HINT.

    Written by: Travis M. Moore
    Last edited: May 29, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import tkinter as tk
from tkinter import font
from tkinter import ttk

##########
# Logger #
##########
# Create new logger
logger = logging.getLogger(__name__)

############
# MainView #
############
class MainView(ttk.Frame):
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        logger.debug("Initializing MainView")

        # Assign attributes
        self.parent = parent
        self.settings = settings
        self.words_dict = {}
        self.buttons_dict = {}
        self.buttonstates_dict = {}

        # Draw widgets
        self._draw_widgets()


    def _draw_widgets(self):
        """ Draw widgets. """
        logger.debug("Drawing MainView widgets")

        ##########
        # Styles #
        ##########
        self.myFont = font.nametofont('TkDefaultFont').configure(size=12)
        options = {'padx':10, 'pady':10}

        style = ttk.Style()
        style.configure('Start.TButton', 
            font=('TkDefaultFont', 10, 'bold'), 
            foreground='green',
            background='black')

        style.configure('Repeat.TButton', 
            font=('TkDefaultFont', 10, 'bold'), 
            foreground='black',
            background='black')

        ##########
        # Frames #
        ##########
        # Main content frame
        frm_main = ttk.Frame(self)
        frm_main.grid(column=5, row=5, sticky='nsew')

        # Words and checkbuttons frame
        self.frm_sentence = ttk.LabelFrame(frm_main, 
                                           text='Sentence:', 
                                           padding=8, 
                                           width=500, 
                                           height=90
                                           )
        self.frm_sentence.grid(column=5, 
                               columnspan=15, 
                               row=5, 
                               sticky='nsew',
                               **options
                               )
        self.frm_sentence.grid_propagate(0)

        # Vertical separator for session info
        sep = ttk.Separator(frm_main, orient='vertical')
        sep.grid(column=20, row=5, rowspan=50, sticky='ns')

        # Session info frame
        self.frm_params = ttk.LabelFrame(frm_main, text="Session Info")
        self.frm_params.grid(column=25, 
                             row=5, 
                             rowspan=15, 
                             sticky='n',
                             **options, 
                             ipadx=5, 
                             ipady=5
                             )

        #######################
        # Session info labels #
        #######################
        # Subject
        ttk.Label(self.frm_params, text="Subject: "
                  ).grid(row=5, column=5, sticky='w')
        ttk.Label(self.frm_params, textvariable=self.settings['subject']
                  ).grid(row=5, column=10, sticky='e')
        # Condition
        ttk.Label(self.frm_params, text="Condition: "
                  ).grid(row=10, column=5, sticky='w')
        ttk.Label(self.frm_params, textvariable=self.settings['condition']
                  ).grid(row=10, column=10, sticky='e')
        # Speaker number
        ttk.Label(self.frm_params, text="Speaker(s): "
                  ).grid(row=15, column=5, sticky='w')
        ttk.Label(self.frm_params, textvariable=self.settings['channel_routing']
                  ).grid(row=15, column=10, sticky='e')
         # List number(s)
        ttk.Label(self.frm_params, text="List(s): "
                  ).grid(row=20, column=5, sticky='w')
        ttk.Label(self.frm_params, textvariable=self.settings['lists']
                  ).grid(row=20, column=10, sticky='e')
        
        # Level
        ttk.Label(self.frm_params, text="Level: "
                  ).grid(row=25, column=5, sticky='w')
        self.lbl_level = ttk.Label(
            self.frm_params, 
            textvariable=self.settings['starting_level_dB']
            )
        self.lbl_level.grid(row=25, column=10, sticky='e')
        
        # Trial number
        ttk.Label(self.frm_params, text="Trial: "
                  ).grid(row=30, column=5, sticky='w')
        self.trial_var = tk.IntVar(value="")
        ttk.Label(self.frm_params, textvariable=self.trial_var
                  ).grid(row=30, column=10, sticky='e')

        #################
        # User controls #
        #################
        # SELECT ALL button
        self.btn_select_all = ttk.Button(frm_main, 
                                         text="Select All", 
                                         state='disabled', 
                                         command=self._on_select_all, 
                                         takefocus=0
                                         )
        self.btn_select_all.grid(row=10, column=5, pady=(0,10))

        # NEXT button
        self.btn_next = ttk.Button(frm_main, 
                                   text="Next", 
                                   state='disabled', 
                                   command=self._on_next,
                                   takefocus=0
                                   )
        self.btn_next.grid(row=15, column=5, pady=(0,10))

        # REPEAT button
        self.btn_repeat = ttk.Button(frm_main, 
                                     text="Repeat",
                                     state='disabled',
                                     command=self._on_repeat, 
                                     takefocus=0, 
                                     )
        self.btn_repeat.grid(row=15, column=6, pady=(0, 10))

    #############
    # Functions #
    #############
    def _reset(self):
        """ Destroy all labels and checkbuttons in main label. 
            Reset all dicts to empty.
        """
        # Destroy labels
        for key in self.words_dict.keys():
            self.words_dict[key].destroy()

        # Destroy boxes
        for key in self.buttons_dict.keys():
            self.buttons_dict[key].destroy()

        # Clear dicts
        self.words_dict = {}
        self.buttons_dict = {}
        self.buttonstates_dict = {}


    def update_main_label(self, sentence):
        """ Update the main label to display the written sentence
            with checkbuttons below key words.
        """
        # Clear main label
        self._reset()

        # Split sentence into list of words
        words = sentence.split()

        # Populate main label
        for ii, word in enumerate(words):
            self.words_dict[ii] = ttk.Label(self.frm_sentence, text=word)
            self.words_dict[ii].grid(row=5, column=ii)
            if word == word.upper():
                self.buttonstates_dict[ii] = tk.IntVar(value=0)
                self.buttons_dict[ii] = ttk.Checkbutton(self.frm_sentence, 
                                text="",
                                takefocus=0,
                                variable=self.buttonstates_dict[ii]
                                )
                self.buttons_dict[ii].grid(row=10, column=ii)


    def enable_user_controls(self, text):
        """ Enable user controls. Set NEXT button text. """
        logger.debug("Enabling user controls")
        self.btn_select_all.config(state='enabled')
        self.btn_next.config(state='enabled')
        self.btn_next.config(text=text)
        self.btn_repeat.config(state='enabled')


    def disable_user_controls(self, text):
        """ Disable user controls. Set NEXT button text. """
        self.btn_next.config(state='disabled')
        self.btn_next.config(text=text)
        self.btn_repeat.config(state='disabled')
        self.btn_select_all.config(state='disabled')


    def update_trial_number(self, trial):
        """ Update the session info 'Trial' label. """
        self.trial_var.set(trial)


    def update_level_source(self):
        """ Switch level label to display current level
            (instead of starting level).
        """
        self.lbl_level.config(textvariable=self.settings['desired_level_dB'])


    def _on_next(self):
        """ Send NEXT event to controller. """
        logger.debug("Sending 'NEXT' event to controller.")
        self.parent.event_generate('<<MainNext>>')


    def _on_select_all(self):
        """ Select all checkboxes convenience function. """
        logger.debug("Selecting all checkbuttons")
        # Set all checkbutton variables to 1 (i.e., selected)
        for ii in self.buttonstates_dict:
            self.buttonstates_dict[ii].set(1)


    def _on_repeat(self):
        """ Repeat the current sentence. """
        logger.debug("Sending REPEAT event to controller")
        self.event_generate('<<MainRepeat>>')
