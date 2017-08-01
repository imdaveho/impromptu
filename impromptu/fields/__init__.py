import platform
from intermezzo import Intermezzo as mzo


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

    def ask(self):
        self._display()
        self._run()
        return None

from ._inputs import TextInput
