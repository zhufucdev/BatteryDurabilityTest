from test import *
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%c', level=logging.DEBUG)

if __name__ == "__main__":
    TestInitialization().carry()
    standard_test = StandardTest()

    standard_test.carry()
