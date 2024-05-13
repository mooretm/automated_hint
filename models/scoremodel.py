""" Score model for automated HINT.

    Written by: Travis M. Moore
    Created: May 10, 2024
    Last edited: May 10, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import statistics

###########
# Logging #
###########
logger = logging.getLogger(__name__)

##############
# ScoreModel #
##############
class ScoreModel:
    def __init__(self):
        """ Instantiate a ScoreModel object. """
        logger.debug("Initializing ScoreModel")


    def _get_word_lists(self, words, button_states):
        """ Loop through checkbutton states (selected/unselected).
            Use indexes of selected/unselected checkbutton states 
            to append actual words from label_dict to correct or
            incorrect lists.
        """
        logger.debug("Getting words marked correct and incorrect")
        correct = []
        incorrect = []
        resp_dict = {'correct': correct, 'incorrect': incorrect}
        for key, value in button_states.items():
            if value.get() == 1:
                resp_dict['correct'].append(
                    words[key].cget('text')
                    )
            elif value.get() == 0:
                resp_dict['incorrect'].append(
                    words[key].cget('text')
                    )
        logger.debug("Correct: %s", resp_dict['correct'])
        logger.debug("Incorrect: %s", resp_dict['incorrect'])

        return resp_dict


    def _get_outcome(self, resp_dict):
        """ Check list of correct/incorrect words to determine
            the overall outcome of the trial.
        """
        logger.debug("Scoring trial")
        # Scoring criterion: all words must have been 
        # correctly identified
        if not resp_dict['incorrect']:
            self.outcome = 1
        else:
            self.outcome = -1
        logger.debug("Outcome: %d", self.outcome)


    def score(self, words, button_states):
        """ Create word lists based on whether they were
            correctly identified or not. Score trial 
            based on any incorrectly identified words.
        """
        # Get lists of correct and incorrect words
        resp_dict = self._get_word_lists(
            words=words,
            button_states=button_states
            )

        # Score the trial (outcome stored in public attribute)
        self._get_outcome(resp_dict)

        # Return resp_dict of words to save to CSV
        return resp_dict


    def get_snr(self, trial_levels, noise_level):
        """ Calculate SNR by averaging levels for trials
            number 5 to the end. Then subtract noise level.
        """
        logger.debug("Calculating final SNR")
        # Average of trials five to end
        avg_level = statistics.mean(trial_levels[4:])
        self.final_snr = avg_level - noise_level


if __name__ == "__main__":
    pass
