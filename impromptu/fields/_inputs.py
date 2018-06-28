from ._base import Question


class BaseInput(Question):
    """
    Base class that includes keyboard input helper functions.
    """
    def __init__(self, name, query, default="", width=120,
                 color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self.TABSTOP = 8
        self.PADDING = 5
        self._visual_offset = 0
        self._cursor_offset = 0
        self._cursor_unicode_offset = 0
        self.config["width"] = width
        self._text = ""

    def _rune_advance(self, r, pos):
        if r == '\t':
            return self.TABSTOP - (pos % self.TABSTOP)
        return self.cli.rune_width(r)

    def _remove(self, text, start, end):
        text = text[:start] + text[end:]
        return text

    def _insert(self, text, offset, what):
        text = text[:offset] + what + text[offset:]
        return text

    def _move_to(self, coffset):
        text = self._text[:coffset]
        voffset = 0
        while len(text) > 0:
            rune = text[0]
            text = text[len(rune):]
            voffset += self._rune_advance(rune, voffset)
        self._cursor_offset = voffset
        self._cursor_unicode_offset = coffset

    def _under_cursor(self):
        return self._text[self._cursor_unicode_offset]

    def _before_cursor(self):
        return self._text[self._cursor_unicode_offset - 1]

    def _move_one_backward(self):
        if self._cursor_unicode_offset == 0:
            return
        size = len(self._before_cursor())
        self._move_to(self._cursor_unicode_offset - size)

    def _move_one_forward(self):
        if self._cursor_unicode_offset == len(self._text):
            return
        size = len(self._under_cursor())
        self._move_to(self._cursor_unicode_offset + size)

    def _move_to_beginning(self):
        self._move_to(0)

    def _move_to_end(self):
        self._move_to(len(self._text))

    def _delete_backward(self):
        if self._cursor_unicode_offset == 0:
            return
        self._move_one_backward()
        size = len(self._under_cursor())
        self._text = self._remove(self._text, self._cursor_unicode_offset,
                                  self._cursor_unicode_offset + size)

    def _delete_forward(self):
        if self._cursor_unicode_offset == len(self._text):
            return
        size = len(self._under_cursor())
        self._text = self._remove(self._text, self._cursor_unicode_offset,
                                  self._cursor_unicode_offset + size)

    def _delete_to_end(self):
        self._text = self._text[:self._cursor_unicode_offset]

    def _insert_rune(self, r):
        self._text = self._insert(self._text, self._cursor_unicode_offset, r)
        self._move_one_forward()

    def _cursorX(self):
        return self._cursor_offset - self._visual_offset

    def _adjust_voffset(self, width):
        ht = self.PADDING
        max_h_threshold = int((width-1)/2)
        if ht > max_h_threshold:
            ht = max_h_threshold
        threshold = width - 1
        if self._visual_offset != 0:
            threshold = width - ht
        if (self._cursor_offset - self._visual_offset) >= threshold:
            self._visual_offset = self._cursor_offset + (ht - width + 1)
        if self._visual_offset != 0 and (self._cursor_offset -
                                         self._visual_offset) < ht:
            self._visual_offset = self._cursor_offset - ht
            if self._visual_offset < 0:
                self._visual_offset = 0


class TextInput(BaseInput):
    def __init__(self, name, query, default="", width=120,
                 color=None, colormap=None):
        super().__init__(name, query, default, width, color, colormap)
        self.widget = "text"
        self.config["prompt"] = (" » ", [(0, 0, 0), (2, 0, 0), (0, 0, 0)])
        self.config["inputs"] = (0, 0, 0)

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "prompt": (*c, default) if type(c) is tuple else (c, default),
            "linespace": (c, default),
            "width": (c, default),
            "inputs": (c, default),
            "result": (c, default),
            "refresh": (c, default),
        }.get(n, None)

    def setup(self, icon=False, prompt=False, inputs=False, linespace=False,
              width=False, result=False, refresh=False):
        kwargs = {
            "icon": icon,
            "prompt": prompt,
            "linespace": linespace,
            "width": width,
            "inputs": inputs,
            "result": result,
            "refresh": refresh,
        }
        super().setup(**kwargs)

    def _draw_prompt(self):
        x, y = 0, self.linenum + 1  # one line below the query
        prompt, colormap = self.config["prompt"]
        for ch, colors in zip(prompt, colormap):
            fg, attr, bg = colors
            self.cli.set_cell(x, y, ch, fg | attr, bg)
            x += 1
        return None

    def _draw_widget(self):
        prompt, _ = self.config["prompt"]
        fg, attr, bg = self.config["inputs"]
        w, h = self.config["width"], 1
        self._adjust_voffset(w)
        t = self._text
        lx, tabstop = 0, 0
        x, y = len(prompt) + 1, self.linenum + h  # one cell after the prompt
        while True:
            rx = lx - self._visual_offset
            if len(t) == 0:
                break
            if lx == tabstop:
                tabstop += self.TABSTOP
            if rx >= w:
                self.cli.set_cell(x+w-1, y, '→', fg | attr, bg)
                break
            rune = t[0]  # TODO: confirm why t[0]
            if rune == '\t':
                while lx < tabstop:
                    rx = lx - self._visual_offset
                    if rx >= w:
                        break  # goto next
                    if rx >= 0:
                        self.cli.set_cell(x+rx, y, ' ', fg | attr, bg)
                    lx += 1
            else:
                if rx >= 0:
                    char = "*" if self.widget == "password" else rune
                    self.cli.set_cell(x+rx, y, char, fg | attr, bg)
                lx += self.cli.rune_width(rune)
            # next:
            t = t[len(rune):]
        if self._visual_offset != 0:
            self.cli.set_cell(x, y, '←', fg | attr, bg)
        return None

    def _clear_widget(self):
        w, h = self.cli.size()
        h = self.config["linespace"]
        for i in range(h):
            y = i + self.linenum + 1
            for x in range(w):
                self.cli.set_cell(x, y, " ", 0, 0)
        return None

    def _redraw_all(self):
        self._clear_widget()
        self._draw_prompt()
        self._draw_widget()
        prompt, _ = self.config["prompt"]
        x, y = len(prompt) + 1, self.linenum + 1
        self.cli.set_cursor(x+self._cursorX(), y)  # TODO: explain this line
        self.cli.flush()

    def reset(self):
        super().reset()
        self._text = ""
        self._visual_offset = 0
        self._cursor_offset = 0
        self._cursor_unicode_offset = 0

    async def _main(self):
        await super()._main()
        self.result = self._text

    async def _handle_events(self):
        evts = self.pull_events()
        if not evts:
            return
        evt = evts[0]
        if evt["Type"] == self.cli.event("Key") and self.evt_mutex == -1:
            k, c = evt["Key"], evt["Ch"]
            if k == self.cli.key("Esc"):
                self.end_signal = True

            elif (k == self.cli.key("CtrlB") or
                  k == self.cli.key("ArrowLeft")):
                self._move_one_backward()

            elif (k == self.cli.key("CtrlF") or
                  k == self.cli.key("ArrowRight")):
                self._move_one_forward()

            elif (k == self.cli.key("Backspace") or
                  k == self.cli.key("Backspace2")):
                self._delete_backward()

            elif (k == self.cli.key("CtrlD") or
                  k == self.cli.key("Delete")):
                self._delete_forward()

            elif k == self.cli.key("Tab"):
                self._insert_rune('\t')

            elif k == self.cli.key("Space"):
                self._insert_rune(' ')

            elif k == self.cli.key("CtrlK"):
                self._delete_to_end()

            elif (k == self.cli.key("Home") or
                  k == self.cli.key("CtrlA")):
                self._move_to_beginning()

            elif (k == self.cli.key("End") or
                  k == self.cli.key("CtrlE")):
                self._move_to_end()

            else:
                # from GoDoc for termbox-go: 'Ch' is invalid
                # if it is 0 when the EventType is 'Key'
                if c != 0:
                    self._insert_rune(chr(c))
        elif evt["Type"] == self.cli.event("Error"):
            # EventError
            raise(Exception(evt["Err"]))
        self._redraw_all()


class PasswordInput(TextInput):
    def __init__(self, name, query, default="", width=120,
                 color=None, colormap=None):
        super().__init__(name, query, default, width, color, colormap)
        self.widget = "password"
