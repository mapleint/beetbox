def controls(status, inp, lock):
    from listener import AudioListener
    from predictor import Predictor
    import numpy as np
    import shared
    listener = AudioListener(calibration_time=6)

    with lock:
        status.value = shared.CALIBRATION

    # Load the saved model
    model_path = 'W2000d100t2e-2_tiny.h5'
    predictor = Predictor(model_path=model_path, k=200, confidence_threshold=0.2, noise_rms=0.02)

    # Start the stream
    print("Starting stream...")
    listener.start_stream()

    # Calibrate noise level
    listener.calibrate()    

    if status.value != shared.QUIT:
        with lock:
            status.value = shared.RUNNING

    # Start listening after calibration
    print("Listening after calibration...")
    try:
        while status.value != shared.QUIT:
            try:
                for audio_chunk in listener.listen():
                    #Predict the label using the audio chunk
                    if status.value == shared.QUIT:
                        exit(0)
                    
                    label = predictor.predict(audio_chunk)
                    if label is not None:
                        with lock:
                            inp.value = label
                        print(f"Predicted label: {label}")
            except OSError as e:
                with lock:
                    status.value = shared.QUIT
                exit(1)
                print(f"Error occurred: {e}. exiting...")

    except KeyboardInterrupt:
        with lock:
            status.value = shared.QUIT
        print("Stopping due to keyboard interrupt...")