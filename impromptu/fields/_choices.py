from platform import system
from functools import reduce
from . import Question


class ChoiceSelect(Question):
    def __init__(self, name, query, choices=[], size=7, settings=None):
        super().__init__(name, query)
        self.QUERY_ICON = ("[?]", (0, self.instance.color("Green"), 0))
        self.CURSOR_ICON = ('›', (self.instance.color("Cyan"),))
        self._prompt = self._config(settings)
        self._padding = size // 2
        self._bottom = len(choices) - 1
        self.widget = "choice"
        self.choices = choices
        self.list_size = size
        self.choice_index = 0
        self.cursor_index = 0

    def _config(self, s):
        coldef = self.instance.color("Default")
        s = {} if s is None else s
        query_icon  = s["query_icon"]  if s.get("query_icon")  else self.QUERY_ICON
        query_color = s["query_color"] if s.get("query_color") else tuple(coldef for _ in self.query)
        cursor_icon = s["cursor_icon"] if s.get("cursor_icon") else self.CURSOR_ICON
        # pair the colors with the strings to be output in the terminal
        return {
            "query": (query_icon[0] + ' ' + self.query,
                      query_icon[1] + (coldef,) + query_color),
            "cursor": (f" {cursor_icon[0]}  ", (coldef,) + cursor_icon[1] + (coldef, coldef)),
            "blanks": tuple(reduce(lambda x,y: x+y, t)
                            for t in zip(*list([(''.join(" "), (coldef,))
                                                for _ in range(len(f" {cursor_icon[0]}  "))])))
        }

    def _draw_prompt(self):
        x, y = 0, self.line
        q = self._prompt["query"]
        coldef = self.instance.color("Default")
        for ch, color in zip(q[0], q[1]):
            self.instance.set_cell(x, y, ch, color, coldef)
            x += 1
        self.instance.set_cell(0, 12, str(self.cursor_index), coldef, coldef)
        self.instance.set_cell(0, 13, str(self.choice_index), coldef, coldef)
        return None

    def _draw_visible_list(self):
        x, y = 0, self.line + 1
        vl = self._make_visible_list()
        coldef = self.instance.color("Default")
        for ch in vl:
            for text, color in zip(ch[0], ch[1]):
                self.instance.set_cell(x, y, text, color, coldef)
                x += 1
            y += 1
            x = 0
        return None

    def _make_visible_list(self):
        segment = []
        length = len(self.choices)
        if (length <= self.list_size):
            segment = self.choices
        else:
            start = self.choice_index - self.cursor_index
            final = self.list_size + start
            segment = self.choices[start:final]
        c, b = self._prompt["cursor"], self._prompt["blanks"]
        coldef = self.instance.color("Default")
        new_list = []
        for i, ch in enumerate(segment):
            if i == self.cursor_index:
                text = c[0] + ch
                color = c[1] + tuple(self.instance.color("Cyan") for _ in ch)
            else:
                text = b[0] + ch
                color = b[1] + tuple(coldef for _ in ch)
            new_list.append((text, color))
        return new_list

    def _clear_all(self):
        coldef = self.instance.color("Default")
        self.instance.clear(coldef, coldef)

    def _redraw_all(self):
        self._clear_all()
        self._draw_prompt()
        self._draw_visible_list()
        self.instance.hide_cursor()
        self.instance.flush()

    def _run(self):
        # check minimum width and height
        # w, h = self.instance.size()
        # do the check here: TODO

        # draw the query and prompt
        self._redraw_all()
        # start the widget
        while True:
            evt = self.instance.poll_event()
            if evt["Type"] == self.instance.event("Key"):
                k, c = evt["Key"], evt["Ch"]
                if k == self.instance.key("Esc"):
                    break
                elif k == self.instance.key("ArrowUp"):
                    if self.cursor_index > self._padding:
                        self.cursor_index -= 1
                        self.choice_index -= 1
                    elif self.choice_index > self._padding:
                        self.choice_index -= 1
                    elif self.choice_index <= self._padding:
                        if self.choice_index > 0:
                            self.choice_index -= 1
                            self.cursor_index -= 1
                        else:
                            self.cursor_index = 0
                elif k == self.instance.key("ArrowDown"):
                    if self.cursor_index < self._padding:
                        self.cursor_index += 1
                        self.choice_index += 1
                    elif self.choice_index < self._bottom - self._padding:
                        self.choice_index += 1
                    elif self.choice_index >= self._bottom - self._padding:
                        if self.choice_index < self._bottom:
                            self.choice_index += 1
                            self.cursor_index += 1
                        else:
                            self.choice_index = self._bottom
                else:
                    pass

            elif evt["Type"] == self.instance.event("Error"):
                # EventError
                raise(Exception(evt["Err"]))
            self._redraw_all()
        self.result = self.choices[self.choice_index]


class MultiSelect(ChoiceSelect):
        # self.FILLED_ICON = ('►' if system() == "Windows" else '◉', mzo.color("Cyan"))
        # self.OPENED_ICON = ('○', mzo.color("Cyan"))


        # filled_icon = s["filled_icon"] if s.get("filled_icon") else self.FILLED_ICON
        # opened_icon = s["opened_icon"] if s.get("opened_icon") else self.OPENED_ICON
    pass
