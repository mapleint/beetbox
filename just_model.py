import multiprocessing as mp
from shared import NONE, CALIBRATION, QUIT

def run_controls(status, inp, lock):
    from controls import controls
    controls(status, inp, lock) 

def main():
    status = mp.Value('i', CALIBRATION)
    inp = mp.Value('i', NONE)
    mutex = mp.Lock()

    control = mp.Process(target=run_controls, args=(status,inp, mutex))
    control.start()
    control.join()

if __name__ == "__main__":
    main()
