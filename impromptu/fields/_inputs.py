from ._base import Question
from impromptu.utils.multimethod import configure


class BaseInput(Question):
    """
    Base class that includes keyboard input helper functions.
    """
    def __init__(self, name, query, default="",
                 color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self.TABSTOP = 8
        self.PADDING = 5
        self.WIDTH = 60
        self._visual_offset = 0
        self._cursor_offset = 0
        self._cursor_unicode_offset = 0
        self._text = ""

    def _rune_advance(self, r, pos):
        if r == '\t':
            return self.TABSTOP - (pos % self.TABSTOP)
        return self.instance.rune_width(r)

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
        self._text = self._remove(self._text, self._cursor_unicode_offset, self._cursor_unicode_offset + size)

    def _delete_forward(self):
        if self._cursor_unicode_offset == len(self._text):
            return
        size = len(self._under_cursor())
        self._text = self._remove(self._text, self._cursor_unicode_offset, self._cursor_unicode_offset + size)

    def _delete_to_end(self):
        self._text = self._text[:self._cursor_unicode_offset]

    def _insert_rune(self, rune):
        self._text = self._insert(self._text, self._cursor_unicode_offset, rune)
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

        if self._visual_offset != 0 and (self._cursor_offset - self._visual_offset) < ht:
            self._visual_offset = self._cursor_offset - ht
            if self._visual_offset < 0:
                self._visual_offset = 0


class TextInput(BaseInput):
    def __init__(self, name, query, default="",
                 color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self.widget = "text"
        self.config["prompt"] = (" » ", [(0,0,0), (2,0,0), (0,0,0)])
        self.config["inputs"] = (0,0,0)

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "prompt": (*c, default) if type(c) is tuple else (c, default),
            "height": (c, default),
            "inputs": (c, default),
            "prehook": (c, default),
            "posthook": (c, default)
        }.get(n, (*default, default))

    def setup(self, icon=False, prompt=False, inputs=False, height=False, prehook=False, posthook=False):
        params = locals()
        for name in params:
            config = params[name]
            if not config or name == 'self':
                continue
            args = self._set_config(name, config)
            self.config[name] = configure(*args)
        return self

    def _draw_prompt(self):
        x, y = 0, self.linenum + 1 # one line below the query
        prompt, colormap = self.config["prompt"]
        for ch, colors in zip(prompt, colormap):
            fg, attr, bg = colors
            self.instance.set_cell(x, y, ch, fg|attr, bg)
            x += 1
        return None

    def _draw_widget(self):
        prompt, _ = self.config["prompt"]
        fg, attr, bg = self.config["inputs"]
        w, h = self.WIDTH, 1
        self._adjust_voffset(w)
        t = self._text
        lx, tabstop = 0, 0
        x, y = len(prompt) + 1, self.linenum + 1 # one cell after the prompt
        while True:
            rx = lx - self._visual_offset
            if len(t) == 0:
                break
            if lx == tabstop:
                tabstop += self.TABSTOP
            if rx >= w:
                self.instance.set_cell(x+w-1, y, '→', fg|attr, bg)
                break
            rune = t[0] # TODO: confirm why t[0]
            if rune == '\t':
                while lx < tabstop:
                    rx = lx - self._visual_offset
                    if rx >= w:
                        break # goto next
                    if rx >= 0:
                        self.instance.set_cell(x+rx, y, ' ', fg|attr, bg)
                    lx += 1
            else:
                if rx >= 0:
                    char = "*" if self.widget == "password" else rune
                    self.instance.set_cell(x+rx, y, char, fg|attr, bg)
                lx += self.instance.rune_width(rune)
            # next:
            t = t[len(rune):]

        if self._visual_offset != 0:
            self.instance.set_cell(x, y, '←', fg|attr, bg)
        return None

    def _clear_widget(self):
        w, h = self.instance.size()
        h = self.config["height"]
        for i in range(h):
            y = i + self.linenum + 1
            for x in range(w):
                self.instance.set_cell(x, y, " ", 0, 0)
        return None

    def _redraw_all(self):
        self._clear_widget()
        self._draw_prompt()
        self._draw_widget()
        prompt, _ = self.config["prompt"]
        x, y = len(prompt) + 1, self.linenum + 1
        self.instance.set_cursor(x+self._cursorX(), y)
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
                elif k == self.instance.key("CtrlB") or k == self.instance.key("ArrowLeft"):
                    self._move_one_backward()
                elif k == self.instance.key("CtrlF") or k == self.instance.key("ArrowRight"):
                    self._move_one_forward()
                elif k == self.instance.key("Backspace") or k == self.instance.key("Backspace2"):
                    self._delete_backward()
                elif k == self.instance.key("CtrlD") or k == self.instance.key("Delete"):
                    self._delete_forward()
                elif k == self.instance.key("Tab"):
                    self._insert_rune('\t')
                elif k == self.instance.key("Space"):
                    self._insert_rune(' ')
                elif k == self.instance.key("CtrlK"):
                    self._delete_to_end()
                elif k == self.instance.key("Home") or k == self.instance.key("CtrlA"):
                    self._move_to_beginning()
                elif k == self.instance.key("End") or k == self.instance.key("CtrlE"):
                    self._move_to_end()
                else:
                    if c != 0:
                        self._insert_rune(chr(c))
            elif evt["Type"] == self.instance.event("Error"):
                # EventError
                raise(Exception(evt["Err"]))
            self._redraw_all()
        self.result = self._text


class PasswordInput(TextInput):
    def __init__(self, name, query, default="",
                 color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self.widget = "password"
