from test import *
import math

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%c', level=logging.DEBUG)


class TestRef:
    def __init__(self, current: Test):
        self.current = current
        self.cancelled = False


def battery_recorder(test_ref: TestRef):
    log = open("record.log", "a")
    log.write("----Battery Duration Test----\n")
    log.write(f"[Start] {time.strftime('%c', time.localtime())}\n")
    log.flush()
    start = time.time()
    while not test_ref.cancelled:
        log.write(f"+{math.floor(time.time() - start)}s"
                  f" {psutil.sensors_battery().percent}% {test_ref.current.current_action}\n")
        log.flush()
        time.sleep(10)
    log.write(f"[Cancelled] {time.strftime('%c', time.localtime())}")
    log.close()


initialization_test = TestInitialization()
standard_test = StandardTest()

ref = TestRef(initialization_test)

if __name__ == "__main__":
    recorder_thread = threading.Thread(target=battery_recorder, args=[ref])

    recorder_thread.start()
    ref.current = initialization_test
    initialization_test.carry()

    ref.current = standard_test
    while True:
        go_on = standard_test.carry()
        if not go_on:
            break
    ref.cancelled = True
