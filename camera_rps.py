'''
Rock-Paper-Scissors is a game in which each player simultaneously shows one of 
three hand signals representing rock, paper, or scissors. Rock beats scissors. 
Scissors beats paper. Paper beats rock. The player who shows the first option 
that beats the other player's option wins. 

This is an implementation of an interactive Rock-Paper-Scissors game, in which 
the user can play with the computer using the camera.

Author: Kristina Gorkovskaya
Date: 2023-04-12
'''

import cv2
from keras.models import load_model
import numpy as np
import random
import time


class KerasModel:
    '''This class is used to represent a trained image classification model.

    Attributes:
        labels_file (str): path to text file containing model labels
        model_file (str): path to h5 file containing model
        tags (list): model labels
        model (keras.engine.sequential.Sequential): model loaded from h5 file
    '''

    def __init__(self, labels_file="labels.txt", model_file="keras_model.h5"):
        '''See help(KerasModel) for accurate signature.'''

        print('Loading image classification model...')
        self.labels_file = labels_file
        self.model_file = model_file
        self.tags = self.read_model_labels()
        self.model = load_model(self.model_file)

    def read_model_labels(self):
        '''Read model labels from input file.
        Input file is expected to contain one model label per row.
        Each label is prefixed with a numeral and a single ASCII space.

        Returns:
            list of strings
        '''
        try:
            with open(self.labels_file, "r") as file:
                tags = [line.strip().split()[1] for line in file.readlines()]
                return tags
        except Exception as err:
            print('Error loading model labels')
            print(err.__class__.__name__, err)

    def predict(self, normalized_image, image_dimensions):
        '''Run the model on an image to predict the likelihood of each class.

        Args:
            normalized_image (numpy.ndarray): numeric representation of model input
            image_dimensions (tuple): width and height of model input

        Returns:
            numpy.ndarray: 1-D array containing probability for each class
        '''

        data = np.ndarray(shape=(1, *image_dimensions, 3), dtype=np.float32)
        data[0] = normalized_image
        prediction = self.model.predict(data)
        return prediction

    def classify(self, prediction):
        '''Classify an image by selecting the class with the highest probability.

        Args:
            prediction (numpy.ndarray): 1-D array containing probabilities of each class

        Returns:
            string: class with highest probability
        '''

        return self.tags[np.argmax(prediction)]


class RockPaperScissors:
    '''This class is used play a game of Rock Paper Scissors against the computer.

    User inputs are sourced via webcam. The webcam captures the user's hand
    gestures and passes them to an image recognition model, which then classifies
    the gestures as "Rock", "Paper", "Scissors", or "Nothing".
    The computer then randomly chooses "Rock", "Paper", or "Scissors"; the user's
    input is compared against the computer's choice to determine a winner.
    The game continues until either the user or the computer reaches a
    pre-determined number of wins.

    Attributes:
        num_wins (int): number of wins that must be reached before game can stop
        model (KerasModel): trained image recognition model
        tags (list of strings): model labels (expected values: "Rock", "Paper", "Scissors", "Nothing")
        cap (cv2.VideoCapture): used for sourcing user inputs via webcam
        computer_choice (str or None): most recent item chosen by computer
        user_choice (str or None): most recent item chosen by user
        frame (numpy.ndarray): numeric representation of current frame captured by webcam
        user_wins (int): number of rounds won by user
        computer_wins (int): number of rounds won by computer
        latest_game_outcome (str): string representation of latest game outcome
    '''

    def __init__(self, model, num_wins=3):
        '''See help(RockPaperScissors) for accurate signature.'''

        print('Starting Rock, Paper, Scissors game...')
        self.model = model
        self.num_wins = num_wins
        self.tags = self.model.tags
        self.cap = cv2.VideoCapture(0)
        self.computer_choice = None
        self.user_choice = None
        self.frame = None
        self.user_wins = 0
        self.computer_wins = 0
        self.latest_game_outcome = ""

    def display_text(self, text, position):
        '''Display text on image capture screen.

        The same text is rendered twice: once in white, and once in
        black with a slightly larger thickness. The white text is then
        overlaid on top of the black text to create white text with a black
        outline for improved visibility.

        Args:
            text (str): line of text to be displayed on screen
            position (tuple): X, Y coordinates where text will be displayed

        Returns:
            None
        '''
        cv2.putText(img=self.frame, text=text, org=position,
                    fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=[0, 0, 0], lineType=cv2.LINE_AA, thickness=4)
        cv2.putText(img=self.frame, text=text, org=position,
                    fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=[255, 255, 255], lineType=cv2.LINE_AA, thickness=2)

    def display_latest_game_outcome(self):
        '''Display the outcome of the latest game on the image capture screen.

        Args:
            None

        Returns: 
            None
        '''

        line_1 = f"Your choice: {self.user_choice}"
        self.display_text(line_1, (50, 100))
        line_2 = f"Computer choice: {self.computer_choice}"
        self.display_text(line_2, (50, 150))
        self.display_text(self.latest_game_outcome, (50, 200))

    def normalize_image(self, image_dimensions):
        '''Normalize current frame captured via webcam, to prepare for classification.

        Args:
            image_dimensions (tuple): image will be resized to these X, Y dimensions

        Returns:
            np.ndarray: resized and normalized image for input into classification model.
        '''
        resized_frame = cv2.resize(self.frame, image_dimensions, interpolation=cv2.INTER_AREA)
        image_np = np.array(resized_frame)
        normalized_image = (image_np.astype(np.float32) / 127.0) - 1
        return normalized_image

    def play(self):
        '''Execute the game play.

        While the specified number of wins has not been reached, 
        (1) Display a countdown timer on the screen
        (2) When countdown ends, read the user's gesture via webcam and
            pass it to the image classification model, which will 
            determine the probability of the gesture being associated with
            each class ("Rock", "Paper", "Scissors", or "Nothing"). 
            Select the class with the highest probability.
        (3) Get the computer's choice by randomly selecting "Rock", "Paper",
            or "Scissors"
        (4) Compare the user's choice against the computer's choice to determine
            who won this round, and update the score accordingly.
        (5) Display the outcome of the game on the screen for a few seconds
            before restarting the countdown and beginning a new iteration 
            of the game.

        Once the specified number of wins has been reached, display the user
        and computer scores on the screen.

        Args:
            None

        Returns:
            None
        '''
        start_time = time.time()
        round_played = False
        image_dimensions = (224, 224)

        try:
            while True:

                if max(self.computer_wins, self.user_wins) >= self.num_wins:
                    self.display_latest_game_outcome()
                    self.display_text("GAME OVER!", (50, 250))
                    self.display_text(f"You: {self.user_wins}", (50, 300))
                    self.display_text(f"Computer: {self.computer_wins}", (50, 350))

                else:

                    _, self.frame = self.cap.read()
                    self.display_text("Press Q to quit", (50, 50))
                    time_elapsed = time.time() - start_time

                    if 1 <= time_elapsed <= 4:
                        countdown_value = 4 - int(time_elapsed)
                        message = f"Get ready to play in {countdown_value}"
                        self.display_text(message, (50, 100))

                    elif 4 < time_elapsed < 7:
                        if not round_played:
                            normalized_image = self.normalize_image(image_dimensions)
                            prediction = self.model.predict(normalized_image, image_dimensions)
                            self.user_choice = self.get_user_choice(prediction)
                            self.computer_choice = self.get_computer_choice()
                            self.latest_game_outcome = self.get_winner()
                            round_played = True
                        else:
                            self.display_latest_game_outcome()

                    elif time_elapsed >= 7:
                        start_time = time.time()
                        round_played = False

                cv2.imshow('frame', self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # After the loop, release the cap object
            # and destroy all the windows
            self.cap.release()
            cv2.destroyAllWindows()

        except Exception as err:
            print('Error executing gameplay')
            print(err.__class__.__name__, err)

    def get_user_choice(self, prediction):
        '''Classify user input as "Rock", "Paper", "Scissors", or "Nothing" based on model output.

        Args:
            prediction (np.ndarray): probabilities associated with each class.

        Returns:
            str: most likely class. If none of the predicted probabilities are above 0.5, 
                 "Nothing" will be returned.
        '''
        if np.max(prediction) >= 0.5:
            return self.model.classify(prediction)
        return "Nothing"

    def get_computer_choice(self):
        '''Randomly select and return "Rock", "Paper", or "Scissors"

        Args:
            None

        Returns:
            str
        '''
        while True:
            choice = random.choice(self.tags)
            if choice != 'Nothing':
                return choice

    def get_winner(self):
        '''Determine winner of current round.

        Compare computer choice against user choice.
        Rock beats scissors, scissors beats paper, paper beats rock.
        Increment self.user_wins if user won this round; 
        increment self.computer_wins of computer won this round.

        Args:
            None

        Returns:
            str: message containing outcome of current round, for display to user.
        '''

        if self.user_choice == "Nothing":
            return "No-one wins"
        elif self.computer_choice == self.user_choice:
            return "It is a tie!"
        else:
            if self.computer_choice == "Rock":
                user_wins_this_round = self.user_choice == "Paper"
            elif self.computer_choice == "Paper":
                user_wins_this_round = self.user_choice == "Scissors"
            else:
                user_wins_this_round = self.user_choice == "Rock"

            if user_wins_this_round:
                self.user_wins += 1
                return "You won!"
            else:
                self.computer_wins += 1
                return "You lost"


if __name__ == '__main__':

    model = KerasModel()
    game = RockPaperScissors(model)
    game.play()
