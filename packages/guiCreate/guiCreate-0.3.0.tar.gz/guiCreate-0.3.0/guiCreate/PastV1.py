import warnings
from os import environ
from threading import Thread

if "PYGAME_HIDE_SUPPORT_PROMPT" in environ:
    import pygame
else:
    environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame

del environ

letters = """qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()'"_+=-/*.?\\|"""


class Var:
    def __init__(self):
        self.DATA = {}

    def __getitem__(self, item):
        return self.DATA.get(item, None)

    def __setitem__(self, key, value):
        self.DATA[key] = value


class ScreenManager:
    def __init__(self, wh: tuple[int, int] = (500, 500), title: str = "My app", icon: str = None, DeprecationWarn=True):
        if DeprecationWarn:
            warnings.warn("ScreenManagerV1 is deprecated. Use ScreenManager instead.", DeprecationWarning, stacklevel=2)
        """
        !!! This was made using pygame !!!

        https://www.pygame.org/contribute.html

        !!! Author Folumo (Ominox_) !!!

        https://folumo.com


        colors:
            color: combinations of red, green and blue including white, gray, black

            HEX: from #000000 to #ffffff

            RGB: from 0, 0, 0 to 255, 255, 255

            (In some situations img:path can be used)


        screens:
            start, all: start and all screen are made on start:

                start screen is automatically opened on run.

                all screen is screen that will show on all screens.


        methods:
            Show: requires id like "screen:start.itemId" show item based on id.

            Hide: requires id like "screen:start.itemId" hides item based on id.

            Delete: requires id like "screen:start.itemId" deletes item based on id.

            ItemExist: requires id like "screen:start.itemId" returns True if item exists.


            Bind: requires key such as "b" and function (every time you click that key function will get run).

            CopyItem: requires item id to be copied and second id destination.


            NewScreen: requires screen name such as "NewScreen" (will not be switched).

            SwitchScreen: requires screen name such as "NewScreen" to be switched.

            DeleteScreen: requires screen name such as "NewScreen" and then it deletes it.


            Rect: Makes rect on screen.

            Text: Makes text on screen.

            Image: Makes img on screen.

            Video: In progress...

            Button: Makes button on screen.


            Thread: Makes thread and runs it.

            IsRunning: Returns True if running.


            OnEveryFrame: runs on every frame (Usually used to render dynamic text).

            NewSize: resizes screen.

            Quit: Quits app/game.

            Mainloop: Runs app/game.


        :param wh: width and width of app.
        :param title: title of app/game.
        :param icon: path to icon for app/game.
        """
        pygame.init()
        pygame.font.init()

        self._wh = wh
        self._cScreen = "screen:start"
        self._running = True
        self._screens = {"screen:start": {}, "screen:all": {}}
        self._root = pygame.display.set_mode(wh)
        self._press = {"keyboard": {"screen:start": {}}, "mouse": {"screen:start": {}}}
        self._onFrame = {}
        self._screenSizes = {"screen:start": wh}

        self.Variables = Var()

        pygame.display.set_caption(title)
        if icon:
            pygame.display.set_icon(pygame.image.load(icon))

    def ItemExist(self, _id: str) -> bool:
        parent, _id = _id.split(".", 1)
        if parent in self._screens:
            return _id in self._screens[parent]
        else:
            raise KeyError("Screen not found in screen manager")

    def OnEveryFrame(self, _id: str, f):
        """
        :param _id: id
        :param f: function.
        :return:
        """

        self._onFrame[_id] = f

    def IsRunning(self):
        """
        Returns True if app is running (usually used in threads).

        :return:
        """
        return self._running

    def Thread(self, f, *args, callback=None, error=None):
        """
        Thread for this app/game.

        :param f: Function to be rum.
        :param args: Args for function.
        :param callback: Function that will be run after execution.
        :param error: Function that will be run if error happens in func f.
        :return:
        """
        Thread(target=lambda: self._startThread(f, *args, callback=callback, error=error)).start()

    def _startThread(self, f, *args, callback, error):
        try:
            f(self, *args)
        except Exception as e:
            if error:
                error(e)

        if callback:
            callback()

    def NewSize(self, _id: str, w: int = 500, h: int = 500):
        """
        Size of new screen.

        :param _id: screen id
        :param w: Width.
        :param h: Height.
        :return:
        """
        if _id in self._screens:
            self._screenSizes[_id] = (w, h)
            self._root = pygame.display.set_mode((w, h))

    def SwitchScreen(self, _id: str):
        """
        Switches to screen.

        :param _id: Needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            if _id in self._screens:
                self._cScreen = _id
                self._root = pygame.display.set_mode(self._screenSizes[_id])

    def DeleteScreen(self, _id: str):
        """
        Deletes screen. (except screen named "all").

        :param _id: Needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            if _id in self._screens:
                del self._screens[f"screen:{_id}"]
                del self._press["keyboard"][_id]
                del self._screenSizes[f"screen:{_id}"]

    def NewScreen(self, _id: str, size=(500, 500)) -> None:
        """
        Makes new screen.

        :param size:
        :param _id: needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            self._screens[f"screen:{_id}"] = {}
            self._press["keyboard"][f"screen:{_id}"] = {}
            self._screenSizes[f"screen:{_id}"] = size

    def Quit(self):
        """
        Quits app/game.

        :return:
        """
        self._running = False

    def CopyItem(self, source_id: str, dest_id: str):
        """
        Copy an item from the source screen to the destination screen.

        :param source_id: The ID of the item to copy (e.g., "screen:start.centerRect").
        :param dest_id: The ID of the destination item (e.g., "screen:main.centerRect").
        """
        source_path = source_id.split(".")
        dest_path = dest_id.split(".")

        # Check if both source and destination screens exist
        if len(source_path) == 2 and len(dest_path) == 2:
            source_screen = source_path[0]
            dest_screen = dest_path[0]

            if source_screen in self._screens and dest_screen in self._screens:
                source_item_id = source_path[1]

                # Check if the source item exists
                if source_item_id in self._screens[source_screen]:
                    source_item = self._screens[source_screen][source_item_id]

                    # Copy the item to the destination screen with a new ID
                    dest_item_id = dest_path[1]
                    self._screens[dest_screen][dest_item_id] = source_item.copy()

                else:
                    raise KeyError(f"Source item '{source_id}' not found.")
            else:
                raise KeyError("Source or destination screen not found.")
        else:
            raise ValueError("Invalid source or destination ID format.")

    def Bind(self, screen: str, key: str, command) -> None:
        """
        Binds screen and key. and executes command when key is pressed.

        :param command: Function or class.
        :param screen: Screen name such as "screen:start".
        :param key: Key as "a", "b", "A" ...
        :return:
        """

        if screen in self._screens == 0:
            if key in letters + ",0123456789 ":
                self._press["keyboard"][screen] = command

    def Rect(self,
             parent, _id: str,
             xy: tuple[int, int] = (0, 0),
             wh: tuple[int, int] = (50, 50),
             _in: str = "color:white",
             show: bool = False
             ) -> None:
        """
        Adds rect to parent and binds it to an id.

        :param show: Should rect be shown on create.
        :param parent: Screen like "screen:start".
        :param _id: String id.
        :param xy: Rect location on screen.
        :param wh: Width and height of rect.
        :param _in: Color of rect.
        :return:
        """
        if parent in self._screens:
            _rect = pygame.Rect(xy, wh)
            self._screens[parent][_id] = {"type": "rect", "data": _rect, "bg": _in, "show": show}
        else:
            raise KeyError("Screen not found in screen manager")

    def _font(self, font, size, text, fg):
        try:
            tmp = pygame.font.Font(font, size)
        except FileNotFoundError:
            tmp = pygame.font.SysFont(font, size)
        return tmp.render(text, True, self._getColor(fg))

    def Image(self, parent, _id, img, xy: tuple[int, int] = (0, 0), wh: tuple[int, int] = None, show: bool = False):
        """
        Adds image to screen and binds it to id.

        :param show: Should image be shown on create.
        :param parent: Screen like "screen:start".
        :param _id: String id.
        :param img: Img path.
        :param xy: Rect location on screen.
        :param wh: Img size (optional).
        :return:
        """

        if parent in self._screens:
            img = pygame.image.load(img)
            if wh:
                img = pygame.transform.scale(img, wh)
            self._screens[parent][_id] = {"type": "img", "data": img, "pos": xy, "show": show}
        else:
            raise KeyError("Screen not found in screen manager")

    def Video(self):
        """
        (Not done yet)
        :return:
        """

    def Text(self,
             font: str = "Arial",
             text: str = "Sample Text.",
             color: str = "color:black",
             size: int = 12
             ) -> pygame.Surface:
        """
        Adds text to parent and binds it to id.

        :param font: System font or path to font.
        :param text: String text.
        :param color: Valid color.
        :param size: Font size.
        :return:
        """
        try:
            return pygame.font.Font(font, size).render(text, False, self._getColor(color))
        except FileNotFoundError:
            try:
                return pygame.font.SysFont(font, size, True).render(text, False, self._getColor(color))
            except ValueError:
                return pygame.font.SysFont("Ariel", 12, True).render("Sample Text", False, self._getColor(color))

    def AddText(self, parent, _id: str, text: pygame.Surface, pos: tuple[int, int] = (0, 0), show: bool = False):
        if parent in self._screens:
            self._screens[parent][_id] = {"type": "text",
                                          "data": text,
                                          "show": show,
                                          "pos": pos}

    def Button(self,
               parent,
               _id: str,
               xy: tuple[int, int] = (0, 0),
               wh: tuple[int, int] = (100, 50),
               _in: str = "color:white",
               _text: pygame.Surface = None,
               command=None,
               show: bool = False
               ) -> None:
        """
        Adds button to parent and binds it to an id.

        :param show: Should button be shown on create.
        :param _text: Get text from Text(...).
        :param parent: Screen like "screen:start".
        :param _id: String id.
        :param xy: Rect location on screen.
        :param wh: Button size.
        :param _in: Can be img or color.
        :param command: Function or class.
        :return:
        """

        if parent in self._screens:
            _rect = pygame.Rect(xy, wh)
            if _in.find("img") == 0:
                d = _in.split(":", 1)[1]
                img = pygame.image.load(d)
                img = pygame.transform.scale(img, wh)
                self._screens[parent][_id] = {"type": "button", "data": img, "command": command, "show": show,
                                              "pos": xy, "rect": _rect, "text": _text}
            else:
                self._screens[parent][_id] = {"type": "button", "data": _rect, "command": command, "show": show,
                                              "bg": _in, "text": _text}

            if _text:
                text_rect = _text.get_rect()
                text_rect.center = _rect.center
                self._screens[parent][_id]["text_rect"] = text_rect

        else:
            raise KeyError("Screen not found in screen manager")

    def Show(self,
             _id: str
             ) -> None:
        """
        Shows item based on the id.

        :param _id: Item id like "screen:start.itemId".
        :return:
        """

        path = _id.split(".", 1)
        if len(path) == 2:
            self._screens[path[0]][path[1]]["show"] = True
        else:
            raise KeyError

    def Hide(self,
             _id: str
             ) -> None:
        """
        Hides item based on the id.

        :param _id: Item id like "screen:start.itemId".
        :return:
        """

        path = _id.split(".", 1)
        if len(path) == 2:
            self._screens[path[0]][path[1]]["show"] = False
        else:
            raise KeyError

    def Delete(self,
               _id: str
               ) -> None:
        """
        Deletes item based on the id.

        :param _id: Item id like "screen:start.itemId".
        :return:
        """

        path = _id.split(".", 1)
        if len(path) == 2:
            del self._screens[path[0]][path[1]]
        else:
            raise KeyError

    def Mainloop(self) -> None:
        """
        This is App/Game main loop that will run inf.
        :return:
        """
        while True:
            try:
                self._mainloop()
                break
            except RuntimeError:
                pass

    def _mainloop(self) -> None:
        """
        This is App/Game main loop that will run inf.
        :return:
        """
        while self._running:
            self._root.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode in self._press["keyboard"][self._cScreen]:
                        self._press["keyboard"][self._cScreen][event.unicode]()
                elif event.type == pygame.MOUSEBUTTONUP:
                    for s in [self._cScreen, "screen:all"]:
                        for item in self._screens[s]:
                            data = self._screens[s][item]
                            if data["type"] == "button":
                                if type(data["data"]) == pygame.Rect:
                                    if data["data"].collidepoint(event.pos):
                                        if data["command"]:
                                            data["command"]({"root": self, "event": event,
                                                             "screen": s, "id": f"{s}.{item}"})
                                else:
                                    if data["rect"].collidepoint(event.pos):
                                        if data["command"]:
                                            data["command"]({"root": self, "event": event,
                                                             "screen": s, "id": f"{s}.{item}"})
            for s in [self._cScreen, "screen:all"]:
                for item in self._screens[s]:
                    data = self._screens[s][item]
                    if data["show"]:
                        if data["type"] == "rect":
                            pygame.draw.rect(self._root, self._getColor(data["bg"]), data["data"])
                        elif data["type"] == "text":
                            self._root.blit(data["data"], data["pos"])
                        elif data["type"] == "button":
                            if type(data["data"]) == pygame.Rect:
                                pygame.draw.rect(self._root, self._getColor(data["bg"]), data["data"])
                                self._root.blit(data["text"], data["text_rect"].topleft)
                            else:
                                self._root.blit(data["data"], data["pos"])
                                self._root.blit(data["text"], data["text_rect"].topleft)
                        elif data["type"] == "img":
                            self._root.blit(data["data"], data["pos"])

            for func in self._onFrame:
                self._onFrame[func](self)

            pygame.display.update()

        pygame.quit()
        pygame.font.quit()

    @staticmethod
    def _getColor(color: str) -> tuple[int, int, int]:
        if color.find("color") == 0:
            color = color.split(":")[1]
            colors = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),

                "purple": (255, 0, 255),
                "yellow": (255, 255, 0),
                "cyan": (0, 255, 255),

                "white": (255, 255, 255),
                "gray": (127, 127, 127),
                "black": (0, 0, 0)
            }
            finalColor = colors.get(color, (0, 0, 0))
        elif color.find("RGB") == 0:
            color = color.split(":")[1]
            safe = True
            for letter in letters:
                if letter in color:
                    safe = False

            if safe:
                finalColor = eval(f"({color})")
            else:
                finalColor = (0, 0, 0)
        elif color.find("HEX") == 0:
            try:
                color = color.split(":")[1]
                red = int(color[1:3], 16)
                green = int(color[3:5], 16)
                blue = int(color[5:7], 16)

                finalColor = (red, green, blue)
            except ValueError:
                finalColor = (0, 0, 0)

        else:
            finalColor = (0, 0, 0)

        return finalColor


def main():
    gui = ScreenManager((700, 500), "my app")

    gui.NewScreen("main")

    gui.Rect("screen:all", "bg", (500, 0), (200, 500), "HEX:#444444", True)

    gui.Rect("screen:start", "bg", (0, 0), (500, 500), "color:gray", True)

    gui.Button("screen:start", "start", (200, 200), (100, 50), "color:white",
               gui.Text(),
               lambda: gui.SwitchScreen("screen:main"),
               True
               )

    gui.Mainloop()


if __name__ == '__main__':
    main()
