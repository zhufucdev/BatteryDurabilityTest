from common import *


class TestInitialization(Test):
    def __init__(self):
        actions = [
            LaunchNeteaseMusic(),
            Pause(2),
            WaitUntilCPUFree(),
            HitSpaceKey(),
            QQLogin()
        ]
        super().__init__("initialize_test", actions)


class StandardTest(Test):
    def __init__(self):
        excel = ExcelPrepare()
        actions = [
            LaunchExcel(),
            WaitUntilCPUFree(),
            Pause(1),
            excel,
            TimerLoop(
                [
                    ExcelCalc(excel),
                    HitEnterKey(),
                    excel.next_row()
                ],
                30
            ),
        ]
        super().__init__("standard_test", actions)
