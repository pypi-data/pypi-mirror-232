from .base import guiBase
from .visible.obj import obj as guiObj
from .noneVisible.obj import obj as nObj


class ScreenManager(guiBase, guiObj, nObj):
    def __init__(self, wh: tuple[int, int] = (500, 500), title: str = "My app", icon: str = None):
        """
        !!! This was made using pygame !!!

        https://www.pygame.org/contribute.html

        !!! Author Folumo (Ominox_) !!!

        https://folumo.com

        id usage example:
            Hide("screen:start.bg")
                -> screen:start is screen id and bg is item id such as Rect or Image

            NewScreen("Main")
                -> here you don't need to use prefix screen:


        colors:
            color: combinations of red, green and blue including white, gray, black

            HEX: from #000000 to #ffffff

            RGB: from 0, 0, 0 to 255, 255, 255

            (In some situations img:path can be used)


        screens:
            screens: start and all are automatically made.
            screen start is screen that you are transferred when run this app/game.
            screen all is screen that will show itself in front of any already visible screens.

            Managing screens: found in .noneVisible.obj.obj
                New screens are made using NewScreen(id, size)
                To change screen size use NewSize(id, w, h)
                To delete a screen use DeleteScreen(id)
                Finally to switch screen use SwitchScreen(id)


        2D Shapes:
            Making 2D shapes: Found in .visible.obj.obj
                Rect(screen, id, xy, wh, in, show)
                Text(font, text, color, size) -> TEXT
                  >> AddText(screen, id, TEXT, xy, show)
                  >> Button(screen, id, xy, wh, in(can be img), TEXT, command, show)
                Image(screen, id, img, xy, wh, show)
                Video() << NOT WORKING (working on)


        App/Game Controls: found in .noneVisible.obj.obj
            Show(id)
            Hide(id)
            Delete(id)

            CopyItem(pos, dest)
            ItemExist(id) -> returns True if item exists.

            Thread(func, *args, callback, error)
            OnEveryFrame(id, func)
            Bind(screen, key, command)

            IsRunning() -> returns True if running (used for inf Threads).
            Quit()

        App/Game main loop:
            Mainloop()
                -> This can't be replaced with anything else it must be on end of code or the app/game wont work !!


        """
        super().__init__(wh=wh, title=title, icon=icon)
        guiObj.__init__(self, self)
        nObj.__init__(self, self)


if __name__ == '__main__':
    gui = ScreenManager()
    gui.Mainloop()
