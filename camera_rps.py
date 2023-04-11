import cv2
from keras.models import load_model
import numpy as np
from typing import Optional
import random
import time


class RockPaperScissors:

    def __init__(self, labels_file: str = "labels.txt", model_file: str = "keras_model.h5"):
        self.model = None
        self.cap = None
        self.data = None
        self.tags = self.read_model_labels(labels_file)
        self.set_up(model_file)
        self.computer_choice = None
        self.user_choice = None
        self.frame = None

    @staticmethod
    def read_model_labels(labels_file: str) -> list:
        try:
            with open(labels_file, "r") as file:
                labels = [line.strip().split()[1] for line in file.readlines()]
                return labels
        except Exception as err:
            print('Error loading model labels')
            print(err.__class__.__name__, err)

    def set_up(self, model_file):
        try:
            self.model = load_model(model_file)
            self.cap = cv2.VideoCapture(0)
            self.data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        except Exception as err:
            print('Error loading model')
            print(err.__class__.__name__, err)

    def display_text(self, text, position):
        font = cv2.FONT_HERSHEY_SIMPLEX
        colour = (0, 255, 255)
        cv2.putText(self.frame, text, position, font, 1, colour, 2, cv2.LINE_4)

    def play(self) -> None:

        start_time = time.time()
        winner_found = False
        result_for_display = ""

        try:
            while True:
                _, self.frame = self.cap.read()
                resized_frame = cv2.resize(
                    self.frame, (224, 224), interpolation=cv2.INTER_AREA)
                image_np = np.array(resized_frame)
                normalized_image = (image_np.astype(np.float32) / 127.0) - 1
                self.data[0] = normalized_image
                prediction = self.model.predict(self.data)

                self.display_text("Press Q to quit", (50, 50))
                time_elapsed = time.time() - start_time

                if 1 <= time_elapsed <= 6:
                    countdown_value = 6 - int(time_elapsed)
                    message = f"Get ready to play in {countdown_value}"
                    self.display_text(message, (50, 100))

                elif 6 < time_elapsed < 10:
                    if not winner_found:
                        self.user_choice = self.get_user_choice(prediction)
                        self.computer_choice = self.get_computer_choice()
                        result_for_display = self.get_winner()
                        winner_found = True
                    else:
                        line_1 = f"Your choice: {self.user_choice}"
                        self.display_text(line_1, (50, 100))
                        line_2 = f"Computer choice: {self.computer_choice}"
                        self.display_text(line_2, (50, 150))
                        self.display_text(result_for_display, (50, 200))

                elif time_elapsed >= 10:
                    start_time = time.time()
                    winner_found = False
                    result_for_display = ""

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

    def get_user_choice(self, prediction: np.array):
        if np.max(prediction) >= 0.95:
            gesture_detected = self.tags[np.argmax(prediction)]
            return gesture_detected
        return "Nothing"

    def get_computer_choice(self):
        '''Randomly select and return "Rock", "Paper", or "Scissors"'''
        while True:
            choice = random.choice(self.tags)
            if choice != 'Nothing':
                return choice

    def get_winner(self):
        '''Compare computer choice against user choice to determine
        who wins the game of rock, paper, scissors.'''

        if self.computer_choice == self.user_choice:
            return "It is a tie!"
        elif self.user_choice == "Nothing":
            return "Null results"
        else:
            if self.computer_choice == "Rock":
                user_wins = self.user_choice == "Paper"
            elif self.computer_choice == "Paper":
                user_wins = self.user_choice == "Scissors"
            else:
                user_wins = self.user_choice == "Rock"

            if user_wins:
                return "You won!"
            return "You lost"


if __name__ == '__main__':

    game = RockPaperScissors()
    game.play()
