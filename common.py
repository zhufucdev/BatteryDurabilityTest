from typing import Sequence, Optional, Iterable, Callable
import logging
import sys
import math
import pyautogui
import pyperclip
import psutil
import threading
import time

IS_WINDOWS = sys.platform == "win32"


class Action:
    """ Symbolize the smallest unit in a test.
    Preferably, use predefined classes.
    """

    def __init__(self, name):
        self.name = name

    def execute(self):
        pass

    def __str__(self):
        return self.name


class AutomaticallyPausedAction(Action):
    """ To distinguish between actions that need pause before executed in action chain and that don't."""

    def __init__(self, name):
        super().__init__(name)


class Test:
    """ Symbolize a test project.
    Use predefined classes preferably.
    """

    def __init__(self, name: str, actions: Iterable[Action]):
        self.name = name
        self.actions = actions

    def carry(self):
        logging.debug(f"------{self}------")
        for action in self.actions:
            try:
                if action is not AutomaticallyPausedAction:
                    Pause(pyautogui.PAUSE).execute()

                logging.debug(f"[{self}] Action: {action}")
                action.execute()
            except pyautogui.FailSafeException as e:
                logging.debug(f"Test cancelled. Cause: {e}")
                sys.exit(1)
            except Exception as e:
                logging.warning(f"Error while carrying out {self}: {e}")

    def __str__(self):
        return self.name


class Pause(Action):
    def __init__(self, amount: float):
        super().__init__("pause")
        self.amount = amount

    def execute(self):
        time.sleep(self.amount)


# Flow Control
class Loop(AutomaticallyPausedAction):
    """ Symbolize a loop, where actions are executed repeatedly in order."""

    def __init__(self, actions: Iterable[Action]):
        super().__init__("loop")
        self.actions = actions

    def execute(self):
        while True:
            for action in self.actions:
                action.execute()


class TimerLoop(Loop):
    """ Symbolize a loop that exits after a certain period of time."""

    def __init__(self, actions: Iterable[Action], timeout: float):
        super().__init__(actions)
        self.timeout = timeout
        self.cancelled = False

    def execute(self):
        time_start = time.time()

        def take(a: Action, timeout: float):
            def execute():
                try:
                    a.execute()
                except pyautogui.FailSafeException:
                    self.cancelled = True

            if a is not AutomaticallyPausedAction:
                time.sleep(pyautogui.PAUSE)

            t = threading.Thread(target=execute)
            t.start()
            logging.debug(f"\t[.loop] Action: {a}")
            t.join(timeout)
            if self.cancelled:
                raise pyautogui.FailSafeException()

            if t.is_alive():
                return False
            return True

        while True:
            for action in self.actions:
                if not take(action, self.timeout - time.time() + time_start):
                    return

    def __str__(self):
        return f"loop(timeout={self.timeout})"


class Batch(AutomaticallyPausedAction):
    """ Symbolize a batch of actions."""

    def __init__(self, name: str, actions: Sequence[Action]):
        super().__init__(name)
        self.actions = actions

    def execute(self):
        for action in self.actions:
            if action is not AutomaticallyPausedAction:
                time.sleep(pyautogui.PAUSE)

            logging.debug(f"\t[.batch] Action: {action}")
            action.execute()

    def __str__(self):
        return f"{self.name}(stack_size={len(self.actions)})"


class WaitUntilCPUFree(Action):
    def __init__(self, strict: Optional[bool] = False):
        super().__init__("wait_for_free")
        self.threshold = 35 - 13 * math.log(psutil.cpu_count(True), math.e * 2)
        if strict:
            self.threshold *= 0.8
        self.timeout = 10

        if self.threshold < 8:
            self.threshold = 8

    def execute(self):
        count = 0
        while psutil.cpu_percent() > self.threshold:
            time.sleep(0.5)
            count += 1
            if count > self.timeout * 2:
                raise TimeoutError(f"CPU usage always high at {psutil.cpu_percent()}%")

    def __str__(self):
        return f"{self.name}(threshold={self.threshold}%)"


class Call(Action):
    def __init__(self, name: str, function: Callable):
        super().__init__(name)
        self.function = function

    def execute(self):
        self.function()


# Common Keys
class HitSearchKey(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("hit_search_key")

    def execute(self):
        if IS_WINDOWS:
            pyautogui.keyDown("win")
            pyautogui.press("s")
            pyautogui.keyUp("win")
        else:
            pyautogui.keyDown("command")
            pyautogui.press("space")
            pyautogui.keyUp("command")


class HitKey(AutomaticallyPausedAction):
    def __init__(self, key_code: str):
        super().__init__(f"hit_{key_code}")
        self.key_code = key_code

    def execute(self):
        pyautogui.press(self.key_code)


class HitSpaceKey(HitKey):
    def __init__(self):
        super().__init__("space")


class HitEnterKey(HitKey):
    def __init__(self):
        super().__init__("enter")


class HitEscapeKey(HitKey):
    def __init__(self):
        super().__init__("esc")


class Paste(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("paste")

    def execute(self):
        if IS_WINDOWS:
            dec = "ctrl"
        else:
            dec = "command"
        pyautogui.keyDown(dec)
        pyautogui.press("v")
        pyautogui.keyUp(dec)


class OpenApp(AutomaticallyPausedAction):
    def __init__(self, app_name: str, interval: Optional[int] = 0.1):
        super().__init__("open_app")
        self.app_name = app_name
        self.interval = interval

    def execute(self):
        HitSearchKey().execute()
        pyautogui.write(self.app_name, self.interval)
        pyautogui.press("enter")

    def __str__(self):
        return f"open_app({self.app_name})"


# App Launcher
class LaunchNeteaseMusic(OpenApp):
    def __init__(self):
        if IS_WINDOWS:
            super().__init__("wangyiyun")
        else:
            super().__init__("neteasemusic")


class LaunchQQ(OpenApp):
    def __init__(self):
        super().__init__("qq")


class MSLaunch(OpenApp):
    def __init__(self, app_name: str):
        self.ms_name = app_name
        super().__init__(app_name, 0)

    def execute(self):
        super().execute()
        if IS_WINDOWS:
            # sometimes Windows has task schedule problem
            WaitUntilCPUFree(strict=True).execute()
            time.sleep(0.5)
            win = pyautogui.getWindowsWithTitle(self.ms_name.title())
            if len(win) < 1:
                raise pyautogui.FailSafeException(f"Failed to activate {self.ms_name.title()}.")
            win[0].activate()


class LaunchExcel(MSLaunch):
    def __init__(self):
        super().__init__("excel")


class LaunchWord(MSLaunch):
    def __init__(self):
        super().__init__("word")


class LaunchPPT(MSLaunch):
    def __init__(self):
        super().__init__("powerpoint")


class LaunchBrowser(MSLaunch):
    def __init__(self):
        if IS_WINDOWS:
            super().__init__("microsoft edge")
        else:
            super().__init__("safari")


class Click(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("click")

    def execute(self):
        pyautogui.click()


# Utility
class MoveCursorRelateToWindow(AutomaticallyPausedAction):
    def __init__(self, x: float, y: float, origin: str):
        self.x = x
        self.y = y
        self.origin = origin
        super().__init__("move_cursor_relatively")

    def execute(self):
        window = pyautogui.getActiveWindow()

        if self.origin[0] == "b":
            y = window.bottom - self.y
        elif self.origin[0] == "c":
            y = window.centery + self.y
        else:
            y = window.top + self.y

        if self.origin[1] == "r":
            x = window.right - self.x
        elif self.origin[1] == "c":
            x = window.centerx + self.x
        else:
            x = window.right + self.x

        pyautogui.moveTo(x, y)


class ClickPos(AutomaticallyPausedAction):
    def __init__(self, pos):
        super().__init__("click_pos")
        self.pos = pos

    def execute(self):
        pyautogui.click(self.pos)


class ClickScreenContent(AutomaticallyPausedAction):
    def __init__(self, sample_name: str, sample_count: Optional[int] = 1):
        super().__init__("click_screen_content")
        self.sample_name = sample_name
        self.successful = False
        if sample_count:
            self.sample_count = sample_count
        else:
            self.sample_count = 1

    def execute(self):
        def click_sample(file):
            pyautogui.click(file)

        if self.sample_count == 1:
            click_sample(f'./samples/{self.sample_name}.png')
        else:
            threads = []
            for i in range(1, self.sample_count + 1):
                t = threading.Thread(target=click_sample, args=[f'./samples/{self.sample_name}.{i}.png'])
                threads.append(t)
                t.start()

            for thread in threads:
                thread.join()

        if not self.successful:
            raise IndexError("Target button is missing.")


class ClickCentral(ClickPos):
    def __init__(self):
        width, height = pyautogui.size()
        super().__init__((width / 2, height / 9))


# Specific Problems
class QQLogin(Batch):
    def __init__(self):
        actions = [
            LaunchQQ(),
            WaitUntilCPUFree(),
            Pause(0.5),
            HitEnterKey(),
            Pause(2),
            WaitUntilCPUFree(),
        ]
        super().__init__("qq_login", actions)


class MSGoto(AutomaticallyPausedAction):
    def __init__(self, address: str):
        super().__init__("ms_goto")
        self.address = address

    def execute(self):
        pyautogui.keyDown("ctrl")
        pyautogui.press("g")
        pyautogui.keyUp("ctrl")
        if not IS_WINDOWS:
            time.sleep(0.5)
            pyautogui.press("tab")
        pyautogui.write(self.address)
        pyautogui.press("enter")
        if not IS_WINDOWS:
            time.sleep(0.5)


class MSOpenRecentDoc(Batch):
    def __init__(self):
        if IS_WINDOWS:
            actions = [
                HitKey("tab")
                for _ in range(0, 4)
            ]
            actions.append(HitEnterKey())
        else:
            actions = [
                HitKey("tab"),
                HitEnterKey()
            ]
        super().__init__("ms_select_first_doc", actions)


class ExcelPrepare(Batch):
    def __init__(self):
        actions = [
            MSOpenRecentDoc(),
            WaitUntilCPUFree(),
            Pause(1),
            MSGoto("BQ3"),
        ]
        self.current_row = 3
        super().__init__("excel_prepare", actions)

    def next_row(self):
        def plus():
            self.current_row += 1

        return Call("bump_row_counter", plus)

    def execute(self):
        super().execute()
        self.current_row = 3


class ExcelCalc(AutomaticallyPausedAction):
    def __init__(self, pre: ExcelPrepare):
        super().__init__("excel_calc")
        self.pre = pre

    def execute(self):
        cells = ",".join([col + str(self.pre.current_row) for col in ['I', 'O', 'U', 'AA', 'AM', 'AS', 'AY', 'BE']])
        expr = f"=SUM({cells})"
        if IS_WINDOWS:
            pyautogui.write(expr)
            time.sleep(0.2)
        else:
            pyperclip.copy(expr)
            pyautogui.keyDown("command")
            pyautogui.press("v")
            pyautogui.keyUp("command")


class PPTPlay(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("ppt_play")

    def execute(self):
        if IS_WINDOWS:
            pyautogui.press("f5")
        else:
            pyautogui.keyDown("command")
            pyautogui.keyDown("shift")
            pyautogui.press("enter")
            pyautogui.keyUp("command")
            pyautogui.keyUp("shift")


class PPTPrepare(Batch):
    def __init__(self):
        actions = [
            MSOpenRecentDoc(),
            WaitUntilCPUFree(),
            Pause(1),
            PPTPlay()
        ]
        self.current_slide = 1
        super().__init__("ppt_prepare", actions)

    def next_slide(self):
        def bump():
            self.current_slide += 1

        return Call("bump_slide_counter", bump)


class PPTNext(AutomaticallyPausedAction):
    def __init__(self, context: PPTPrepare):
        super().__init__("ppt_next")
        self.context = context

    def execute(self):
        time.sleep(5)
        if self.context.current_slide >= 65:  # Sample PPT's actual click count
            pyautogui.press("esc")
            self.context.current_slide = 1
            PPTPlay().execute()
        else:
            pyautogui.press("enter")


class WordTypeNonsense(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("word_typewrite")

    def execute(self):
        pyautogui.write("Microsoft Word the best IDE on this planet! ", 0.08)
        time.sleep(0.5)
        pyautogui.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        pyautogui.press("enter")


class OpenNewTab(AutomaticallyPausedAction):
    def __init__(self):
        super().__init__("open_new_tab")

    def execute(self):
        if IS_WINDOWS:
            dec = "ctrl"
        else:
            dec = "command"
        pyautogui.keyDown(dec)
        pyautogui.press("t")
        pyautogui.keyUp(dec)


class BrowsePage(TimerLoop):
    def __init__(self, timeout: float):
        def scroll():
            width, height = pyautogui.size()
            if IS_WINDOWS:
                amount = 15
            else:
                amount = -15
            pyautogui.scroll(amount, width / 2, height / 2)

        actions = [
            Call("scroll", scroll),
            Pause(1)
        ]
        super().__init__(actions, timeout)


class OpenAndBrowse(Batch):
    def __init__(self, url: str, timeout: float):
        self.url = url

        def copy_url():
            pyperclip.copy(url)

        actions = [
            OpenNewTab(),
            Call("copy_url", copy_url),
            Paste(),
            HitEnterKey(),
            WaitUntilCPUFree(strict=True),
            BrowsePage(timeout)
        ]
        super().__init__("browse_web", actions)
