from platform import system
from functools import reduce
from . import Question


class ChoiceSelect(Question):
    def __init__(self, name, query, choices=[], size=7, **settings):
        super().__init__(name, query, **settings)
        self._padding = size // 2
        self._bottom = len(choices) - 1
        self.widget = "choice"
        self.choices = choices
        self.list_size = size
        self.choice_index = 0
        self.cursor_index = 0
        self.cursor = ('›', (self.instance.color("Cyan"),))

    def _make_segment_list(self):
        segment = []
        length = len(self.choices)
        if (length <= self.list_size):
            segment = self.choices
        else:
            start = self.choice_index - self.cursor_index
            final = self.list_size + start
            segment = self.choices[start:final]
        return segment

    def _make_visible_list(self):
        segment = self._make_segment_list()
        c = self.symbols.get("cursor") or self.cursor
        cursor = (f" {c[0]}  ", (self.clr,) + c[1] + (self.clr, self.clr))
        blanks = tuple(reduce(lambda x,y: x+y, t) for t in zip(*list([
            (''.join(" "), (self.clr,)) for _ in f" {c[0]}  "])))
        new_list = []
        for i, ch in enumerate(segment):
            if i == self.cursor_index:
                text = cursor[0] + ch
                color = cursor[1] + tuple(self.instance.color("Cyan") for _ in ch)
            else:
                text = blanks[0] + ch
                color = blanks[1] + tuple(self.clr for _ in ch)
            new_list.append((text, color))
        return new_list

    def _draw_widget(self):
        x, y = 0, self.line + 1
        vl = self._make_visible_list()
        for ch in vl:
            for text, color in zip(ch[0], ch[1]):
                self.instance.set_cell(x, y, text, color, self.clr)
                x += 1
            y += 1
            x = 0
        return None

    def _clear_widget(self):
        w, h = self.instance.size()
        h = self.list_size
        for i in range(h):
            y = i + self.line + 1
            for x in range(w):
                self.instance.set_cell(x, y, " ", self.clr, self.clr)
        return None

    def _redraw_all(self):
        self._clear_widget()
        self._draw_widget()
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
