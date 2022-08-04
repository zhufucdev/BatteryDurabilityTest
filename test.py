from common import *

MS_WORK_DURATION = 10
DEFAULT_BROWSING_TIME = 30
TOTAL_BROWSING_TIME = 30
BROWSE_PAGES = ["jd.com", "taobao.com", "sina.com.cn", "163.com", "sohu.com", ("ithome.com", 20), ("chiphell.com", 10),
                ("bbs.nga.cn", 10), ("gamersky.com", 15), ("3dmgame.com", 20), ("4399.com", 23),
                ("https://www.apple.com.cn/macbook-air-m2/", 80)]
VIDEO_WATCH_TIME = 30
QQ_CHAT_TIME = 30


class TestInitialization(Test):
    def __init__(self):
        actions = [
            LaunchNeteaseMusic(),
            Pause(2),
            WaitUntilCPUFree(strict=True),
            HitSpaceKey(),
            QQLogin()
        ]
        super().__init__("initialize_test", actions)


class StandardTest(Test):
    def __init__(self):
        excel_context = ExcelPrepare()
        ppt_context = PPTPrepare()
        word_context = WordPrepare()
        web_browsing = [LaunchBrowser()]
        for page in BROWSE_PAGES:
            if type(page) is tuple:
                site, duration = page
                web_browsing.append(OpenAndBrowse(site, duration))
            else:
                web_browsing.append(OpenAndBrowse(page, DEFAULT_BROWSING_TIME))
        web_browsing.append(SearchWithBaiduAndBrowse("Geekerwan", 20))
        web_browsing.append(Quit())
        actions = [
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

            word_context,
            Pause(1),
            TimerLoop([WordTypeNonsense()], MS_WORK_DURATION),

            Pause(1),
            TimerLoop(web_browsing, TOTAL_BROWSING_TIME, should_not_stop_when=['quit']),
            OpenAndBrowse("https://www.bilibili.com/video/BV1Af4y1f7NJ", 0),
            Pause(VIDEO_WATCH_TIME),
            Quit(),

            WakeQQ(),
            WaitUntilCPUFree(),
            BotChat(QQ_CHAT_TIME),
            Pause(1),
            CloseWindow()
        ]

        super().__init__("standard_test", actions)
