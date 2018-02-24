from platform import system
from ._base import Question
from impromptu.utils.multimethod import configure


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
            "height": (c, default)
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
        segment = self._segment_choices()
        choices = [(c, [inactive for _ in c]) for c in segment]
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
    def __init__(self, name, query, choices=None, size=7,
                 default="", color=None, colormap=None):
        super().__init__(name, query, choices, size, default, color, colormap)
        self.widget = "multi-choice"
        self.choices = [(c, False) for c in choices]
        self.config["cursor"] = (" › ", [(0,0,0), (7,0,0), (0,0,0)])
        self.config["selected"] = "► " if system() == "Windows" else "◉ "
        self.config["unselected"] = '○ '

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "cursor": (*c, default) if type(c) is tuple else (c, default),
            "selected": (c, default),
            "unselected": (c, default),
            "active": (c, default),
            "inactive": (c, default),
            "height": (c, default),
        }.get(n, (*default, default))

    def setup(self, icon=False, cursor=False, selected=False,
              unselected=False, active=False, inactive=False,
              height=False):
        params = locals()
        for name in params:
            config = params[name]
            if not config or name == 'self':
                continue
            args = self._set_config(name, config)
            self.config[name] = configure(*args)
        return self

    def _prepare_choices(self):
        active = self.config["active"]
        inactive = self.config["inactive"]
        cursor, cursor_cm = self.config["cursor"]
        selected = self.config["selected"]
        unselected = self.config["unselected"]
        choices = self._segment_choices()
        blanks = ''.join([" " for _ in cursor])
        blanks_cm = [inactive for _ in blanks]
        render_list = []
        for i, c in enumerate(choices):
            render = None
            choice, is_checked = c
            if i == self.cursor_index:
                if is_checked:
                    text = cursor + selected + choice
                else:
                    text = cursor + unselected + choice
                colormap = [active for _ in text]
                render = (text, colormap)
            else:
                if is_checked:
                    text = blanks + selected + choice
                    colormap = [active for _ in text]
                else:
                    text = blanks + unselected + choice
                    colormap = [inactive for _ in text]
                render = (text, colormap)
            render_list.append(render)
        return render_list

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
                elif k == self.instance.key("ArrowRight"):
                    choice, _ = self.choices[self.choice_index]
                    self.choices[self.choice_index] = (choice, True)
                elif k == self.instance.key("ArrowLeft"):
                    choice, _ = self.choices[self.choice_index]
                    self.choices[self.choice_index] = (choice, False)
                elif k == self.instance.key("Space"):
                    choice, marked = self.choices[self.choice_index]
                    self.choices[self.choice_index] = (choice, not marked)
                else:
                    pass

            elif evt["Type"] == self.instance.event("Error"):
                # EventError
                raise(Exception(evt["Err"]))
            self._redraw_all()
        self.result = [ch for ch, s in self.choices if s]
