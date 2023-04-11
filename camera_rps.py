import cv2
from keras.models import load_model
import numpy as np
from typing import Optional


class ComputerVisionModel:

    def __init__(self, labels_file: str = "labels.txt", model_file: str = "keras_model.h5"):
        self.model = None
        self.cap = None
        self.data = None
        self.tags = self.read_model_labels(labels_file)
        self.load_model(model_file)

    @staticmethod
    def read_model_labels(labels_file: str) -> dict:
        try:
            with open(labels_file, "r") as file:
                labels = [line.strip().split() for line in file.readlines()]
                return {int(label[0]): label[1] for label in labels}
        except Exception as err:
            print('Error loading model labels')
            print(err.__class__.__name__, err)

    def load_model(self, model_file: str) -> None:
        try:
            self.model = load_model(model_file)
            self.cap = cv2.VideoCapture(0)
            self.data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        except Exception as err:
            print('Error loading model')
            print(err.__class__.__name__, err)

    def interpret_prediction(self, prediction: np.array) -> Optional[str]:
        if np.max(prediction) >= 0.95:
            gesture_detected = self.tags[np.argmax(prediction)]
            if gesture_detected != 'Nothing':
                return gesture_detected
        return None

    def predict(self) -> Optional[str]:
        try:
            while True:
                _, frame = self.cap.read()
                resized_frame = cv2.resize(
                    frame, (224, 224), interpolation=cv2.INTER_AREA)
                image_np = np.array(resized_frame)
                normalized_image = (image_np.astype(np.float32) / 127.0) - 1
                self.data[0] = normalized_image
                prediction = self.model.predict(self.data)
                if (gesture_detected := self.interpret_prediction(prediction)):
                    return gesture_detected
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return None

        except Exception as err:
            print('Error getting user choice')
            print(err.__class__.__name__, err)

    def exit(self) -> None:
        # After the loop, release the cap object
        # and destroy all the windows
        self.cap.release()
        cv2.destroyAllWindows()


def get_prediction() -> str:
    input_reader = ComputerVisionModel()
    choice = input_reader.predict()
    input_reader.exit()
    return choice


if __name__ == '__main__':

    prediction = get_prediction()
    print(prediction)
