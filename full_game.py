import multiprocessing as mp
from shared import NONE, CALIBRATION 

def run_controls(status, inp, lock):
    from controls import controls
    controls(status, inp, lock) 

def run_menu(status, inp, lock):
    from menu import menu
    menu(status, inp, lock)

def main():
    status = mp.Value('i', CALIBRATION)
    inp = mp.Value('i', NONE)
    mutex = mp.Lock()

    control = mp.Process(target=run_controls, args=(status,inp, mutex))
    #menu = mp.Process(target=run_menu, args=(status,inp, lock))

    control.start()
    run_menu(status, inp, mutex)

    control.join()
    #menu.join()

if __name__ == "__main__":
    main()