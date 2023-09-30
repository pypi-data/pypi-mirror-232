from os import environ

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


class guiBase:
    def __init__(self, wh: tuple[int, int] = (500, 500), title: str = "My app", icon: str = None):
        pygame.init()
        pygame.font.init()

        self.wh = wh
        self.cScreen = "screen:start"
        self.running = True
        self.screens = {"screen:start": {}, "screen:all": {}}
        self.AppRoot = pygame.display.set_mode(wh)
        self.press = {"keyboard": {"screen:start": {}}, "mouse": {"screen:start": {}}}
        self.onFrame = {}
        self.screenSizes = {"screen:start": wh}

        self.Variables = Var()

        pygame.display.set_caption(title)
        if icon:
            pygame.display.set_icon(pygame.image.load(icon))

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
        while self.running:
            self.AppRoot.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.unicode in self.press["keyboard"][self.cScreen]:
                        self.press["keyboard"][self.cScreen][event.unicode]()
                elif event.type == pygame.MOUSEBUTTONUP:
                    for s in [self.cScreen, "screen:all"]:
                        for item in self.screens[s]:
                            data = self.screens[s][item]
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
            for s in [self.cScreen, "screen:all"]:
                for item in self.screens[s]:
                    data = self.screens[s][item]
                    if data["show"]:
                        if data["type"] == "rect":
                            pygame.draw.rect(self.AppRoot, self.getColor(data["bg"]), data["data"])
                        elif data["type"] == "text":
                            self.AppRoot.blit(data["data"], data["pos"])
                        elif data["type"] == "button":
                            if type(data["data"]) == pygame.Rect:
                                pygame.draw.rect(self.AppRoot, self.getColor(data["bg"]), data["data"])
                                self.AppRoot.blit(data["text"], data["text_rect"].topleft)
                            else:
                                self.AppRoot.blit(data["data"], data["pos"])
                                self.AppRoot.blit(data["text"], data["text_rect"].topleft)
                        elif data["type"] == "img":
                            self.AppRoot.blit(data["data"], data["pos"])

            for func in self.onFrame:
                self.onFrame[func](self)

            pygame.display.update()

        pygame.quit()
        pygame.font.quit()

    @staticmethod
    def getColor(color: str) -> tuple[int, int, int]:
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
