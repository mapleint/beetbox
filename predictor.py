import numpy as np
import tensorflow as tf

class Predictor:
    def __init__(self, model_path, input_shape=(2000, 1), k=200, confidence_threshold=0.97, noise_rms=0.05, b=30):
        """
        Initializes the Predictor with the loaded model and parameters for RMS checking.
        
        Parameters:
        - model_path: path to the trained CNN model
        - input_shape: shape of the input expected by the CNN (default is (5000, 1))
        - k: size of the sharp checker chunk for RMS check (default is 1/10th of W)
        - confidence_threshold: minimum confidence to accept a prediction (default 0.97)
        - noise_rms: RMS threshold to determine significant sound (default 0.05)
        - b: number of buffers to skip after a successful prediction
        """
        self.model = tf.keras.models.load_model(model_path)
        self.input_shape = input_shape  # Ensure chunks match the CNN's input size
        self.k = k
        self.confidence_threshold = confidence_threshold
        self.noise_rms = noise_rms
        self.b = b  # Number of buffers to skip after a successful prediction
        self.skip_counter = 0  # Counter to track skipped buffers

    def rms(self, audio_chunk):
        """Calculate the RMS (Root Mean Square) of the audio chunk."""
        return np.sqrt(np.mean(audio_chunk ** 2))

    def prepare_input(self, audio_chunk):
        """Prepares the input chunk for the CNN."""
        # Reshape or pad to match CNN input (assuming mono-channel input)
        audio_chunk = np.expand_dims(audio_chunk, axis=-1)  # Add a channel dimension
        if audio_chunk.shape[0] < self.input_shape[0]:
            padding = np.zeros((self.input_shape[0] - audio_chunk.shape[0], 1))
            audio_chunk = np.concatenate((audio_chunk, padding), axis=0)
        elif audio_chunk.shape[0] > self.input_shape[0]:
            audio_chunk = audio_chunk[:self.input_shape[0], :]
        
        return np.expand_dims(audio_chunk, axis=0)  # Add batch dimension

    def predict(self, audio_chunk):
        """
        Predicts the sound label if the RMS check passes.
        
        Parameters:
        - audio_chunk: the raw audio chunk to process
        
        Returns:
        - label: predicted label if the confidence threshold is met, else None
        """

        # If within the "blindness" period, skip the buffer processing
        if self.skip_counter > 0:
            self.skip_counter -= 1
            # print(f"Skipping buffer, remaining blindness buffers: {self.skip_counter}")
            return None

        # Perform the sharp checker RMS test on the first k samples
        sharp_checker_chunk = audio_chunk[:self.k]
        rms_value = self.rms(sharp_checker_chunk)

        # Run CNN only if RMS exceeds noise threshold
        if rms_value > self.noise_rms:
            # Prepare the input for the CNN
            prepared_input = self.prepare_input(audio_chunk)

            # Get the prediction from the model
            prediction = self.model.predict(prepared_input)
            y_max = np.max(prediction)  # Maximum confidence value in the prediction
            label = np.argmax(prediction, axis=1)[0]  # Label with highest probability
            
            # Only return label if confidence exceeds the threshold
            if y_max >= self.confidence_threshold:
                # Enter the "blindness" period where the next b buffers will be skipped
                self.skip_counter = self.b
                # print(f"Prediction made with confidence {y_max}. Entering blindness for {self.b} buffers.")
                return label
            else:
                # print(f"Fake CNN run, confidence: {y_max}")
                return None
        else:
            # print(f"RMS {rms_value} below noise threshold {self.noise_rms}")
            return None
