from common import *

MS_WORK_DURATION = 30


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
        excel_context = ExcelPrepare()
        ppt_context = PPTPrepare()
        actions = [
            LaunchExcel(),
            WaitUntilCPUFree(),
            Pause(1),
            excel_context,
            Pause(1),
            TimerLoop(
                [
                    ExcelCalc(excel_context),
                    HitEnterKey(),
                    excel_context.next_row()
                ],
                MS_WORK_DURATION
            ),
            Pause(0.5),
            HitEscapeKey(),

            LaunchPPT(),
            WaitUntilCPUFree(),
            Pause(1),
            ppt_context,
            Pause(1),
            TimerLoop(
                [
                    PPTNext(ppt_context),
                    ppt_context.next_slide()
                ],
                MS_WORK_DURATION
            ),
            Pause(0.5),
            HitEscapeKey(),

            LaunchWord(),
            WaitUntilCPUFree(),
            Pause(1),
            MSOpenRecentDoc(),
            Pause(1),
            TimerLoop([WordTypeNonsense()], MS_WORK_DURATION)
        ]
        super().__init__("standard_test", actions)
