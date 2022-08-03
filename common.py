from typing import List, Optional
import logging
import sys
import pyautogui
import threading
import time

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%c')

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


class Test:
    """ Symbolize a test project.
    Use predefined classes preferably.
    """

    def __init__(self, name: str, actions: List[Action]):
        self.name = name
        self.actions = actions

    def carry(self):
        for action in self.actions:
            try:
                action.execute()
            except Exception as e:
                logging.warning(f"Error while executing action {action} in {self}: {e}")

    def __str__(self):
        return self.name


class Pause(Action):
    def __init__(self, amount: float):
        super().__init__("pause")
        self.amount = amount

    def execute(self):
        time.sleep(self.amount)


class HitSearchKey(Action):
    def __init__(self):
        super().__init__("hit_search_key")

    def execute(self):
        if IS_WINDOWS:
            pyautogui.press("win")
        else:
            pyautogui.keyDown("command")
            pyautogui.press("space")
            pyautogui.keyUp("command")


class HitSpaceKey(Action):
    def __init__(self):
        super().__init__("play")

    def execute(self):
        pyautogui.press("space")


class OpenApp(Action):
    def __init__(self, app_name: str):
        super().__init__("open_app")
        self.app_name = app_name

    def execute(self):
        HitSearchKey().execute()
        pyautogui.write(self.app_name, 0.1)
        pyautogui.press("enter")

    def __str__(self):
        return f"open_app({self.app_name})"


class LaunchNeteaseMusic(OpenApp):
    def __init__(self):
        if IS_WINDOWS:
            super().__init__("wangyiyun")
        else:
            super().__init__("neteasemusic")


class ClickScreenContent(Action):
    def __init__(self, sample_name: str, sample_count: Optional[int]):
        super().__init__("click_screen_content")
        self.sample_name = sample_name
        self.successful = False
        if sample_count:
            self.sample_count = sample_count
        else:
            self.sample_count = 1

    def execute(self):
        def click_sample(file):
            btn_location = pyautogui.locateOnScreen(file)
            if btn_location is not None:
                x, y = pyautogui.center(btn_location)
                pyautogui.click(x, y)
                self.successful = True

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


class MoveCursorRelateToWindow(Action):
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


class Click(Action):
    def __init__(self):
        super().__init__("click")

    def execute(self):
        pyautogui.click()


class TestInitialization(Test):
    def __init__(self):
        actions = [
            LaunchNeteaseMusic(),
            Pause(8),
            HitSpaceKey()
        ]
        super().__init__("initialize_test", actions)


class StandardTest(Test):
    def __init__(self):
        actions = [

        ]

        super().__init__("standard_test", actions)
