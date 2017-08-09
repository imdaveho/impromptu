from platform import system
from intermezzo import Intermezzo as mzo


class Impromptu(object):
    def __init__(self):
        self._toggle_on = (
            '►' if system() == "Windows"
            else '◉', mzo.color("Cyan")
        )
        self._toggle_off = ('○', mzo.color("Cyan"))
        self._query_icon = ("[?]", (0, mzo.color("Green"), 0))
        self._text_icon = ("»", mzo.color("Red"))
        self._list_icon = ('›', mzo.color("Cyan"))
        self.active_index = 0
        self.query_list = []

    def add(self, name, query, widget, theme=None):
        self.query_list.append(locals())

    def _init(self):
        pass
    def _prompt(self):
        pass
    def _loop(self):
        pass

    def ask(self):
        # initialize
        err = mzo.init()
        if err:
            raise(Exception(err))
        mzo.set_input_mode(mzo.input("Esc"))
        # draw loop
        for i, q in enumerate(self.query_list):
            x, y = 0, self.active_index
            widget = q["widget"]
            
        # end loop and close
        mzo.close()



class Question(object):
    def __init__(self, name, query, config=None):
        self._os = platform.system()
        self.name = name
        self.query = query
        self.template = self._config(config)
        self.line = 0
        self.result = ""
        self.instance = mzo

    def _config(self, conf):
        if conf is None:
            conf = {}
        query = conf.get("query") or "[?]"
        prompt = conf.get("prompt") or "»"
        toggle, untoggle = '◉', '◯'
        if self._os == "Windows":
            toggle, untoggle = '►', '○' # or toggle: '•'
        toggle = conf.get("toggle") or toggle
        untoggle = conf.get("untoggle") or untoggle
        selector = conf.get("selector") or '›'
        template = {
            "query": f"{query} ",
            "prompt": f" {prompt} ",
            "toggle": f"{toggle} ",
            "untoggle": f"{untoggle} ",
            "selector": f" {selector} "
        }
        return template

    def _display(self):
        pass

    def _run(self):
        pass

    def set_line(self, linenum):
        self.line = linenum
        return None

    def ask(self):
        self._display()
        self._run()
        return None

from ._inputs import TextInput, PasswordInput
