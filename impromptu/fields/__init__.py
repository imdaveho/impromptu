from platform import system
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
        # draw loop
        # for i, q in enumerate(self.query_list):
        #     x, y = 0, self.active_index
        self.query_list[0]._run()
        # end loop and close
        mzo.close()


class Question(object):
    """
    A question holds render configuration as well as the order
    for which question to render next in either direction.
    """

    def __init__(self, name, query):
        self.instance = mzo
        self.line = 0
        self.result = ""
        self.name = name
        self.query = query

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
