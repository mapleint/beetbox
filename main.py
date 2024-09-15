from listener import AudioListener
from predictor import Predictor
import numpy as np

def main():
    listener = AudioListener()

    # Load the saved model
    model_path = 'W2000d100t2e-2_tiny.h5'
    predictor = Predictor(model_path=model_path, k=200, confidence_threshold=0.7, noise_rms=0.08)

    # Start the stream
    print("Starting stream...")
    listener.start_stream()

    # Calibrate noise level
    listener.calibrate()

    # Start listening after calibration
    print("Listening after calibration...")
    try:
        while True:
            try:
                for audio_chunk in listener.listen():
                    # Predict the label using the audio chunk
                    label = predictor.predict(audio_chunk)
                    if label is not None:
                        print(f"Predicted label: {label}")
            except OSError as e:
                print(f"Error occurred: {e}. Continuing to listen...")
                continue  # Continue listening after handling the error

    except KeyboardInterrupt:
        print("Stopping due to keyboard interrupt...")

if __name__ == "__main__":
    main()
