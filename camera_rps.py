import cv2
from keras.models import load_model
import numpy as np
from typing import Optional
import random
import time


class KerasModel:

    def __init__(self, labels_file="labels.txt", model_file="keras_model.h5"):
        self.tags = self.read_model_labels(labels_file)
        self.model = load_model(model_file)

    @staticmethod
    def read_model_labels(labels_file):
        try:
            with open(labels_file, "r") as file:
                labels = [line.strip().split()[1] for line in file.readlines()]
                return labels
        except Exception as err:
            print('Error loading model labels')
            print(err.__class__.__name__, err)

    def predict(self, normalized_image, image_dimensions):
        data = np.ndarray(shape=(1, *image_dimensions, 3), dtype=np.float32)
        data[0] = normalized_image
        prediction = self.model.predict(data)
        return prediction

    def classify(self, prediction):
        return self.tags[np.argmax(prediction)]


class RockPaperScissors:

    def __init__(self, num_rounds=3, labels_file="labels.txt", model_file="keras_model.h5"):
        self.model = KerasModel(labels_file, model_file)
        self.tags = self.model.tags
        self.cap = cv2.VideoCapture(0)
        self.computer_choice = None
        self.user_choice = None
        self.frame = None
        self.user_wins = 0
        self.computer_wins = 0
        self.num_rounds = num_rounds

    def display_text(self, text, position):
        font = cv2.FONT_HERSHEY_SIMPLEX
        colour = (0, 255, 255)
        cv2.putText(self.frame, text, position, font, 1, colour, 2, cv2.LINE_4)

    def normalize_image(self, image_dimensions):
        resized_frame = cv2.resize(self.frame, image_dimensions, interpolation=cv2.INTER_AREA)
        image_np = np.array(resized_frame)
        normalized_image = (image_np.astype(np.float32) / 127.0) - 1
        return normalized_image

    def play(self):

        start_time = time.time()
        winner_found = False
        result_for_display = ""
        image_dimensions = (224, 224)

        try:
            while True:

                if max(self.computer_wins, self.user_wins) >= self.num_rounds:
                    self.display_text("GAME OVER!", (50, 250))
                    self.display_text(f"You: {self.user_wins}", (50, 300))
                    self.display_text(f"Computer: {self.computer_wins}", (50, 350))

                else:

                    _, self.frame = self.cap.read()
                    self.display_text("Press Q to quit", (50, 50))
                    time_elapsed = time.time() - start_time

                    if 1 <= time_elapsed <= 6:
                        countdown_value = 6 - int(time_elapsed)
                        message = f"Get ready to play in {countdown_value}"
                        self.display_text(message, (50, 100))

                    elif 6 < time_elapsed < 10:
                        if not winner_found:
                            normalized_image = self.normalize_image(image_dimensions)
                            prediction = self.model.predict(normalized_image, image_dimensions)
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
        if np.max(prediction) >= 0.5:
            return self.model.classify(prediction)
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

    game = RockPaperScissors()
    game.play()
