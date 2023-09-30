import pygame

from ..base import guiBase


class obj:
    def __init__(self, root: guiBase):
        self.root = root

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
        if parent in self.root.screens:
            _rect = pygame.Rect(xy, wh)
            self.root.screens[parent][_id] = {"type": "rect", "data": _rect, "bg": _in, "show": show}
        else:
            raise KeyError("Screen not found in screen manager")

    def _font(self, font, size, text, fg):
        try:
            tmp = pygame.font.Font(font, size)
        except FileNotFoundError:
            tmp = pygame.font.SysFont(font, size)
        return tmp.render(text, True, self.root.getColor(fg))

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

        if parent in self.root.screens:
            img = pygame.image.load(img)
            if wh:
                img = pygame.transform.scale(img, wh)
            self.root.screens[parent][_id] = {"type": "img", "data": img, "pos": xy, "show": show}
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
            return pygame.font.Font(font, size).render(text, False, self.root.getColor(color))
        except FileNotFoundError:
            try:
                return pygame.font.SysFont(font, size, True).render(text, False, self.root.getColor(color))
            except ValueError:
                return pygame.font.SysFont("Ariel", 12, True).render("Sample Text", False, self.root.getColor(color))

    def AddText(self, parent, _id: str, text: pygame.Surface, pos: tuple[int, int] = (0, 0), show: bool = False):
        if parent in self.root.screens:
            self.root.screens[parent][_id] = {"type": "text",
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

        if parent in self.root.screens:
            _rect = pygame.Rect(xy, wh)
            if _in.find("img") == 0:
                d = _in.split(":", 1)[1]
                img = pygame.image.load(d)
                img = pygame.transform.scale(img, wh)
                self.root.screens[parent][_id] = {"type": "button", "data": img, "command": command, "show": show,
                                                  "pos": xy, "rect": _rect, "text": _text}
            else:
                self.root.screens[parent][_id] = {"type": "button", "data": _rect, "command": command, "show": show,
                                                  "bg": _in, "text": _text}

            if _text:
                text_rect = _text.get_rect()
                text_rect.center = _rect.center
                self.root.screens[parent][_id]["text_rect"] = text_rect

        else:
            raise KeyError("Screen not found in screen manager")
