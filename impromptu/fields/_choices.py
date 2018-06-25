from platform import system
from ._base import Question


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
        cursor_colormap = [(0, 0, 0), (7, 0, 0), (0, 0, 0), (0, 0, 0)]
        self.config["cursor"] = (" ›  ", cursor_colormap)
        self.config["active"] = (7, 0, 0)
        self.config["inactive"] = (0, 0, 0)

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "cursor": (*c, default) if type(c) is tuple else (c, default),
            "active": (c, default),
            "inactive": (c, default),
            "height": (c, default),
            "result": (c, default),
            "refresh": (c, default),
        }.get(n, None)

    def setup(self, icon=False, cursor=False, active=False, inactive=False,
              height=False, result=False, refresh=False):
        kwargs = {
            "icon": icon,
            "cursor": cursor,
            "active": active,
            "inactive": inactive,
            "height": height,
            "result": result,
            "refresh": refresh,
        }
        super().setup(**kwargs)

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
                self.cli.set_cell(x, y, ch, fg | attr, bg)
                x += 1
            y += 1
            x = 0
        return None

    def _clear_widget(self):
        w, h = self.cli.size()
        h = self.size
        for i in range(h):
            y = i + self.linenum + 1
            for x in range(w):
                self.cli.set_cell(x, y, " ", 0, 0)
        return None

    def _redraw_all(self):
        self._clear_widget()
        self._draw_widget()
        self.cli.hide_cursor()
        self.cli.flush()

    def reset(self):
        super().reset()
        self.choice_index = 0
        self.cursor_index = 0

    async def _main(self):
        await super()._main()
        self.result = self.choices[self.choice_index]

    async def _handle_events(self):
        evts = self.pull_events()
        if not evts:
            return
        evt = evts[0]
        if evt["Type"] == self.cli.event("Key"):
            k = evt["Key"]
            if k == self.cli.key("Esc"):
                self.end_signal = True
            elif k == self.cli.key("ArrowUp"):
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
            elif k == self.cli.key("ArrowDown"):
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
        elif evt["Type"] == self.cli.event("Error"):
            # EventError
            raise(Exception(evt["Err"]))
        self._redraw_all()


class MultiSelect(ChoiceSelect):
    def __init__(self, name, query, choices=None, size=7,
                 default="", color=None, colormap=None):
        super().__init__(name, query, choices, size, default, color, colormap)
        self.widget = "multi-choice"
        self.choices = [(c, False) for c in choices]
        cursor_colormap = [(0, 0, 0), (7, 0, 0), (0, 0, 0)]
        self.config["cursor"] = (" › ", cursor_colormap)
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
            "result": (c, default),
            "refresh": (c, default),
        }.get(n, None)

    def setup(self, icon=False, cursor=False, selected=False, unselected=False,
              active=False, inactive=False, height=False, result=False,
              refresh=False):
        kwargs = {
            "icon": icon,
            "cursor": cursor,
            "selected": selected,
            "unselected": unselected,
            "active": active,
            "inactive": inactive,
            "height": height,
            "result": result,
            "refresh": refresh,
        }
        # have to call the base Question class
        # since MultiSelect extends ChoiceSelect
        # and ChoiceSelect has different kwargs
        # than what the MultiSelect can accept
        super(ChoiceSelect, self).setup(**kwargs)

    def _prepare_choices(self):
        active = self.config["active"]
        inactive = self.config["inactive"]
        cursor, cursor_cm = self.config["cursor"]
        selected = self.config["selected"]
        unselected = self.config["unselected"]
        choices = self._segment_choices()
        blanks = ''.join([" " for _ in cursor])
        # blanks_cm = [inactive for _ in blanks]  # TODO: confirm usage
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

    def reset(self):
        super().reset()
        reset_choices = []
        for c, _ in self.choices:
            reset_choices.append(c, False)
        self.choices = reset_choices

    async def _main(self):
        await super()._main()
        self.result = [ch for ch, s in self.choices if s]

    async def _handle_events(self):
        evts = self.pull_events()
        if not evts:
            return
        evt = evts[0]
        if evt["Type"] == self.cli.event("Key"):
            k = evt["Key"]
            if k == self.cli.key("Esc"):
                self.end_signal = True
            elif k == self.cli.key("ArrowUp"):
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
            elif k == self.cli.key("ArrowDown"):
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
            elif k == self.cli.key("ArrowRight"):
                choice, _ = self.choices[self.choice_index]
                self.choices[self.choice_index] = (choice, True)
            elif k == self.cli.key("ArrowLeft"):
                choice, _ = self.choices[self.choice_index]
                self.choices[self.choice_index] = (choice, False)
            elif k == self.cli.key("Space"):
                choice, marked = self.choices[self.choice_index]
                self.choices[self.choice_index] = (choice, not marked)
            else:
                pass

        elif evt["Type"] == self.cli.event("Error"):
            # EventError
            raise(Exception(evt["Err"]))
        self._redraw_all()
