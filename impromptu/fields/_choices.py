from platform import system
from . import Question
from ._utils import configure


class ChoiceSelect(Question):
    def __init__(self, name, query, choices=None, size=7,
                 default="", color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self.PADDING = size // 2
        self.widget = "choice"
        self.size = size
        self.choice_index = 0
        self.cursor_index = 0
        if choices is None:
            self.choices = []
            self.BOTTOM = 0
        else:
            self.choices = choices
            self.BOTTOM = len(choices) - 1
        self.config["cursor"] = (" ›  ", [(0,0,0), (7,0,0), (0,0,0), (0,0,0)])
        self.config["active"] = (7,0,0)
        self.config["inactive"] = (0,0,0)

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "cursor": (*c, default) if type(c) is tuple else (c, default),
            "active": (c, default),
            "inactive": (c, default),
            "height": (c, default),
            "choices": (c, default) # TODO: update configure to support
        }.get(n, (*default, default))

    def setup(self, icon=False, cursor=False, choices=False,
                    active=False, inactive=False, height=False):
        params = locals()
        for name in params:
            config = params[name]
            if not config or name == 'self':
                continue
            args = self._set_config(name, config)
            self.config[name] = configure(*args)
        return self

    def _segment_choices(self):
        segment = []
        length = len(self.choices)
        if (length <= self.size):
            segment = self.choices
        else:
            start = self.choice_index - self.cursor_index
            finish = self.size + start
            segment = self.choices[start:finish]
        return segment

    def _prepare_choices(self):
        active = self.config["active"]
        inactive = self.config["inactive"]
        choices = [(c, [inactive for _ in c])
                   for c in self._segment_choices()]
        cursor, cursor_cm = self.config["cursor"]
        blanks = ''.join([" " for _ in cursor])
        blanks_cm = [inactive for _ in cursor_cm]
        render_list = []
        for i, c in enumerate(choices):
            render = None
            choice, choice_cm = c
            if i == self.cursor_index:
                choice_cm = [active for _ in choice]
                render = (cursor + choice, cursor_cm + choice_cm)
            else:
                render = (blanks + choice, blanks_cm + choice_cm)
            render_list.append(render)
        return render_list

    def _draw_widget(self):
        x, y = 0, self.linenum + 1
        renderable = self._prepare_choices()
        for choice in renderable:
            c, cm = choice
            for ch, colors in zip(c, cm):
                fg, attr, bg = colors
                self.instance.set_cell(x, y, ch, fg|attr, bg)
                x += 1
            y += 1
            x = 0
        return None

    def _clear_widget(self):
        w, h = self.instance.size()
        h = self.size
        for i in range(h):
            y = i + self.linenum + 1
            for x in range(w):
                self.instance.set_cell(x, y, " ", 0, 0)
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
                    if self.cursor_index > self.PADDING:
                        self.cursor_index -= 1
                        self.choice_index -= 1
                    elif self.choice_index > self.PADDING:
                        self.choice_index -= 1
                    elif self.choice_index <= self.PADDING:
                        if self.choice_index > 0:
                            self.choice_index -= 1
                            self.cursor_index -= 1
                        else:
                            self.cursor_index = 0
                elif k == self.instance.key("ArrowDown"):
                    if self.cursor_index < self.PADDING:
                        self.cursor_index += 1
                        self.choice_index += 1
                    elif self.choice_index < self.BOTTOM - self.PADDING:
                        self.choice_index += 1
                    elif self.choice_index >= self.BOTTOM - self.PADDING:
                        if self.choice_index < self.BOTTOM:
                            self.choice_index += 1
                            self.cursor_index += 1
                        else:
                            self.choice_index = self.BOTTOM
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
