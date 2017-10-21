from intermezzo import Intermezzo as mzo


class Impromptu(object):
    def __init__(self):
        self.active_index = 0
        self.query_list = []

    def add(self, question):
        self.query_list.append(question)

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
        mzo.set_output_mode(mzo.output("256"))
        # draw loop
        # for i, q in enumerate(self.query_list):
        #     x, y = 0, self.active_index
        # =================================================
        self.query_list[0]._prompt()
        self.query_list[0]._run()
        self.query_list[0]._clear_all()
        self.query_list[0]._prompt()
        for i, ch in enumerate(self.query_list[0].result):
            x = len(self.query_list[0].query) + i + 5
            y = self.query_list[0].line
            mzo.set_cell(x, y, ch, 240, 0)
        # =================================================
        self.query_list[1].line = 3
        self.query_list[1]._prompt()
        self.query_list[1]._run()
        # end loop and close
        mzo.close()


class Question(object):
    """
    A question holds render configuration as well as the order
    for which question to render next in either direction.

    :param name: <str> Identify the question
    :param query: <str> Content of the question
    :param **settings: <dict> Configuration for the question
    """

    def __init__(self, name, query, **settings):
        self.instance = mzo
        self.line = 0
        self.result = ""
        self.name = name
        self.query = query
        self.height = 2
        self.clr = mzo.color("Default")
        self.icon = ("[?]", (0, mzo.color("Green"), 0))
        self.symbols = settings.get("symbols") or {}
        self.jumps = settings.get("jumps") or []
        self.rules = settings.get("rules") or []

    def _prompt(self):
        x, y = 0, self.line
        icon = self.symbols.get("icon") or self.icon
        prompt = (icon[0] + f" {self.query}",
                  icon[1] + tuple(self.clr for _ in f" {self.query}"))
        for ch, color in zip(prompt[0], prompt[1]):
            self.instance.set_cell(x, y, ch, color, self.clr)
            x += 1
        return None

    def _clear_all(self):
        coldef = self.instance.color("Default")
        self.instance.clear(coldef, coldef)

    def _run(self):
        pass

    def set_line(self, linenum):
        self.line = linenum
        return None

    def ask(self):
        self._prompt()
        self._run()
        return None

from ._inputs import TextInput, PasswordInput
from ._choices import ChoiceSelect
