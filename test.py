from common import *

MS_WORK_DURATION = 30
BROWSE_PAGES = ["jd.com", "taobao.com", "sina.com.cn", "163.com", "sohu.com", "ithome.com", "chiphell.com",
                "bbs.nga.cn", "gamersky.com", "3dmgame.com", "4399.com", "https://www.apple.com.cn/macbook-air-m2/"]


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
            Pause(1.3),
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
            Pause(1.3),
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
            Pause(1.3),
            MSOpenRecentDoc(),
            Pause(1),
            TimerLoop([WordTypeNonsense()], MS_WORK_DURATION),

            Pause(1),
            LaunchBrowser()
        ]
        [actions.append(OpenAndBrowse(url, 10)) for url in BROWSE_PAGES]
        super().__init__("standard_test", actions)
