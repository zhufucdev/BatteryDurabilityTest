from test import *
import logging
import pyautogui

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%c', level=logging.DEBUG)

if __name__ == "__main__":
    TestInitialization().carry()
    StandardTest().carry()
