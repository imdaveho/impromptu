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
        self.cursor = '›'

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
        cyan = self.instance.color("Cyan")
        cc = self.colors.get("cursor") or cyan
        tg = self.colors.get("toggled") or cyan
        ug = self.colors.get("untoggled") or self.fgcol
        cursor = (f" {c}  ", (self.fgcol, cc, self.fgcol, self.fgcol))
        blanks = tuple(reduce(lambda x,y: x+y, t) for t in zip(*list([
            (''.join(" "), (self.fgcol,)) for _ in f" {c}  "])))
        new_list = []
        for i, ch in enumerate(segment):
            if i == self.cursor_index:
                text = cursor[0] + ch
                color = cursor[1] + tuple(tg for _ in ch)
            else:
                text = blanks[0] + ch
                color = blanks[1] + tuple(ug for _ in ch)
            new_list.append((text, color))
        return new_list

    def _draw_widget(self):
        x, y = 0, self.line + 1
        vl = self._make_visible_list()
        for ch in vl:
            for text, color in zip(ch[0], ch[1]):
                self.instance.set_cell(x, y, text, color, self.bgcol)
                x += 1
            y += 1
            x = 0
        return None

    def _clear_widget(self):
        clear = self.instance.color("Default")
        w, h = self.instance.size()
        h = self.list_size
        for i in range(h):
            y = i + self.line + 1
            for x in range(w):
                self.instance.set_cell(x, y, " ", clear, clear)
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
    def __init__(self, name, query, choices=[], size=7, **settings):
        super().__init__(name, query, choices, size, **settings)
        self.widget = "multiple"
        self.choices = [(ch, False) for ch in choices]
        self.filled = '►' if system() == "Windows" else '◉'
        self.opened = '○'

    def _make_visible_list(self):
        segment = self._make_segment_list()
        # get symbols
        c = self.symbols.get("cursor") or self.cursor
        f = self.symbols.get("filled") or self.filled
        o = self.symbols.get("opened") or self.opened
        # get colors
        cyan = self.instance.color("Cyan")
        cc = self.colors.get("cursor") or cyan
        tg = self.colors.get("toggled") or cyan
        ug = self.colors.get("untoggled") or self.fgcol
        # configure text/color pairs
        cursor = (f" {c}", (self.fgcol, cc))
        blanks = tuple(reduce(lambda x,y: x+y, t) for t in zip(*list([
            (''.join(" "), (self.fgcol,)) for _ in f" {c}"])))
        filled = (f"{f} ", (tg, self.fgcol))
        normal = (f"{o} ", (ug, self.fgcol))
        select = (f"{o} ", (tg, self.fgcol))
        new_list = []
        for i, ch in enumerate(segment):
            tx = ch[0]
            if i == self.cursor_index: # cursor on item
                if ch[1]: # toggled
                    text = cursor[0] + filled[0] + tx
                    color = cursor[1] + filled[1] + tuple(tg for _ in tx)
                else: # untoggled
                    text = cursor[0] + select[0] + tx
                    color = cursor[1] + select[1] + tuple(tg for _ in tx)
            else:
                if ch[1]:
                    text = blanks[0] + filled[0] + tx
                    color = blanks[1] + filled[1] + tuple(tg for _ in tx)
                else:
                    text = blanks[0] + normal[0] + tx
                    color = blanks[1] + normal[1] + tuple(ug for _ in tx)
            new_list.append((text, color))
        return new_list

    def _run(self):
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
                elif k == self.instance.key("ArrowRight"):
                    # new_choices = []
                    # for i, ch in enumerate(self.choices):
                    #     if i == self.choice_index:
                    #         new_choices.append((ch[0], True))
                    #     else:
                    #         new_choices.append(ch)
                    # self.choices = new_choices
                    ch = self.choices[self.choice_index]
                    self.choices[self.choice_index] = (ch[0], True)
                elif k == self.instance.key("ArrowLeft"):
                    # new_choices = []
                    # for i, ch in enumerate(self.choices):
                    #     if i == self.choice_index:
                    #         new_choices.append((ch[0], False))
                    #     else:
                    #         new_choices.append(ch)
                    # self.choices = new_choices
                    ch = self.choices[self.choice_index]
                    self.choices[self.choice_index] = (ch[0], False)
                elif k == self.instance.key("Space"):
                    # new_choices = []
                    # for i, ch in enumerate(self.choices):
                    #     if i == self.choice_index:
                    #         if ch[1]:
                    #             new_ch = (ch[0], False)
                    #         else:
                    #             new_ch = (ch[0], True)
                    #         new_choices.append(new_ch)
                    #     else:
                    #         new_choices.append(ch)
                    # self.choices = new_choices
                    ch = self.choices[self.choice_index]
                    if ch[1]:
                        self.choices[self.choice_index] = (ch[0], False)
                    else:
                        self.choices[self.choice_index] = (ch[0], True)
                else:
                    pass

            elif evt["Type"] == self.instance.event("Error"):
                # EventError
                raise(Exception(evt["Err"]))
            self._redraw_all()
        # self.result = self.choices[self.choice_index]
