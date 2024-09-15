# import pyaudio
# import numpy as np
# import time

# class AudioListener:
#     def __init__(self, W=2000, d=220, rate=44100, calibration_time=10):
#         self.W = W  # Number of latest indices to process
#         self.d = d  # Interval in ticks (ticks are based on rate)
#         self.rate = rate  # Sample rate
#         self.calibration_time = calibration_time  # Calibration time in seconds
#         self.audio_interface = pyaudio.PyAudio()
#         self.stream = None
#         self.max_signal = None  # Maximum signal during calibration
#         self.audio_buffer = np.array([])  # Buffer to store incoming audio

#     def start_stream(self):
#         self.stream = self.audio_interface.open(
#             format=pyaudio.paInt16,  # 16-bit integer format
#             channels=1,              # Mono input
#             rate=self.rate,
#             input=True,
#             frames_per_buffer=self.d  # Reading d=220 ticks at a time
#         )

#     def calibrate(self):
#         """Record the first t=10 seconds and get the max signal during calibration."""
#         print(f"Starting calibration for {self.calibration_time} seconds...")
#         start_time = time.time()
#         max_signal = 0

#         while time.time() - start_time < self.calibration_time:
#             audio_data = self.stream.read(self.d)
#             audio_np = np.frombuffer(audio_data, dtype=np.int16)
#             max_signal = max(max_signal, np.abs(audio_np).max())  # Track the max absolute value

#         self.max_signal = max_signal  # Save the max signal for normalization
#         print(f"Calibration done. Max signal: {self.max_signal}")

#     def listen(self):
#         """Start listening and yield the latest W=2000 indices every d=220 ticks."""
#         if self.max_signal is None:
#             raise ValueError("Calibration must be done before listening to audio.")

#         while True:
#             # Read new audio data of size d=220
#             audio_data = self.stream.read(self.d)
#             audio_np = np.frombuffer(audio_data, dtype=np.int16)

#             # Normalize the incoming data
#             normalized_audio = audio_np / self.max_signal if self.max_signal != 0 else audio_np

#             # Append the normalized audio to the buffer
#             self.audio_buffer = np.append(self.audio_buffer, normalized_audio)

#             # If buffer exceeds W (2000 samples), trim it to the latest W samples
#             if len(self.audio_buffer) > self.W:
#                 self.audio_buffer = self.audio_buffer[-self.W:]

#             # Yield the latest W samples every d ticks
#             if len(self.audio_buffer) == self.W:
#                 print(f"Yielding normalized chunk with mean: {self.audio_buffer.mean()}")
#                 yield self.audio_buffer

#     def stop_stream(self):
#         self.stream.stop_stream()
#         self.stream.close()
#         self.audio_interface.terminate()

import pyaudio
import numpy as np
import time

class AudioListener:
    def __init__(self, W=2000, d=220, rate=44100, calibration_time=10):
        self.W = W  # Number of latest indices to process
        self.d = d  # Interval in ticks (ticks are based on rate)
        self.rate = rate  # Sample rate
        self.calibration_time = calibration_time  # Calibration time in seconds
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.max_signal = None  # Maximum signal during calibration
        self.audio_buffer = np.array([])  # Buffer to store incoming audio

    def start_stream(self):
        self.stream = self.audio_interface.open(
            format=pyaudio.paInt16,  # 16-bit integer format
            channels=1,              # Mono input
            rate=self.rate,
            input=True,
            frames_per_buffer=self.d  # Reading d=220 ticks at a time
        )

    def calibrate(self):
        """Record the first t=10 seconds and get the max signal during calibration."""
        print(f"Starting calibration for {self.calibration_time} seconds...")
        start_time = time.time()
        max_signal = 0

        while time.time() - start_time < self.calibration_time:
            audio_data = self.stream.read(self.d)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            max_signal = max(max_signal, np.abs(audio_np).max())  # Track the max absolute value

        self.max_signal = max_signal  # Save the max signal for normalization
        print(f"Calibration done. Max signal: {self.max_signal}")

    def listen(self):
        """Start listening and yield the latest W=2000 indices every d=220 ticks."""
        if self.max_signal is None:
            raise ValueError("Calibration must be done before listening to audio.")

        last_yield_time = time.time()

        while True:
            # Read new audio data of size d=220
            audio_data = self.stream.read(self.d)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)

            # Normalize the incoming data
            normalized_audio = audio_np / self.max_signal if self.max_signal != 0 else audio_np

            # Append the normalized audio to the buffer
            self.audio_buffer = np.append(self.audio_buffer, normalized_audio)

            # print(len(self.audio_buffer))

            # If buffer exceeds W (2000 samples), trim it to the latest W samples
            if len(self.audio_buffer) > self.W:
                self.audio_buffer = self.audio_buffer[-self.W:]
            
            # Yield the latest W samples every d ticks
            if len(self.audio_buffer) == self.W:
                current_time = time.time()
                elapsed_time = current_time - last_yield_time
                last_yield_time = current_time

                # print(f"Yielding chunk. Elapsed time: {elapsed_time:.6f} seconds (Expected: {self.d/self.rate:.6f} seconds)")
                yield self.audio_buffer

    # def stop_stream(self):
    #     self.stream.stop_stream()
    #     self.stream.close()
    #     self.audio_interface.terminate()