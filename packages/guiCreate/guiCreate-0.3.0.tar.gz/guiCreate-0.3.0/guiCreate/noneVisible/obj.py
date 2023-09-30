from threading import Thread

import pygame

from ..base import guiBase

letters = """qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()'"_+=-/*.?\\|"""


class obj:
    def __init__(self, root: guiBase):
        self.root = root

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
            self.root.screens[path[0]][path[1]]["show"] = True
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
            self.root.screens[path[0]][path[1]]["show"] = False
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
            del self.root.screens[path[0]][path[1]]
        else:
            raise KeyError

    def ItemExist(self, _id: str) -> bool:
        parent, _id = _id.split(".", 1)
        if parent in self.root.screens:
            return _id in self.root.screens[parent]
        else:
            raise KeyError("Screen not found in screen manager")

    def OnEveryFrame(self, _id: str, f):
        """
        :param _id: id
        :param f: function.
        :return:
        """

        self.root.onFrame[_id] = f

    def IsRunning(self):
        """
        Returns True if app is running (usually used in threads).

        :return:
        """
        return self.root.running

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
        if _id in self.root.screens:
            self.root.screenSizes[_id] = (w, h)
            self.root.AppRoot = pygame.display.set_mode((w, h))

    def SwitchScreen(self, _id: str):
        """
        Switches to screen.

        :param _id: Needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            if _id in self.root.screens:
                self.root.cScreen = _id
                self.root.AppRoot = pygame.display.set_mode(self.root.screenSizes[_id])

    def DeleteScreen(self, _id: str):
        """
        Deletes screen. (except screen named "all").

        :param _id: Needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            if _id in self.root.screens:
                del self.root.screens[f"screen:{_id}"]
                del self.root.press["keyboard"][_id]
                del self.root.screenSizes[f"screen:{_id}"]

    def NewScreen(self, _id: str, size=(500, 500)) -> None:
        """
        Makes new screen.

        :param size:
        :param _id: needs to be like "MyScreen".
        :return:
        """
        if _id != "all":
            self.root.screens[f"screen:{_id}"] = {}
            self.root.press["keyboard"][f"screen:{_id}"] = {}
            self.root.screenSizes[f"screen:{_id}"] = size

    def Quit(self):
        """
        Quits app/game.

        :return:
        """
        self.root.running = False

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

            if source_screen in self.root.screens and dest_screen in self.root.screens:
                source_item_id = source_path[1]

                # Check if the source item exists
                if source_item_id in self.root.screens[source_screen]:
                    source_item = self.root.screens[source_screen][source_item_id]

                    # Copy the item to the destination screen with a new ID
                    dest_item_id = dest_path[1]
                    self.root.screens[dest_screen][dest_item_id] = source_item.copy()

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

        if screen in self.root.screens == 0:
            if key in letters + ",0123456789 ":
                self.root.press["keyboard"][screen] = command
