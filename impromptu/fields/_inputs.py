from . import Question


class BaseInput(Question):
    """
    Base class that includes keyboard input helper functions.
    """
    def __init__(self, name, query):
        super().__init__(name, query)
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
    def __init__(self, name, query, settings=None):
        super().__init__(name, query)
        self.QUERY_ICON = ("[?]", (0, self.instance.color("Green"), 0))
        self.INPUT_ICON = ("»", (self.instance.color("Red"),))
        self._prompt = self._config(settings)
        self.widget = "text"
        self.height = 2

    def _config(self, s):
        coldef = self.instance.color("Default")
        query_icon   = s["query_icon"]  if s.get("query_icon") else self.QUERY_ICON
        query_color  = s["query_color"] if s.get("query_color") else tuple(coldef for _ in self.query)
        input_icon   = s["input_icon"]  if s.get("input_icon") else self.INPUT_ICON
        return {
            "query": (query_icon[0] + ' ' + self.query,
                      query_icon[1] + (coldef,) + query_color),
            "input": (f" {input_icon[0]} ", (coldef,) + input_icon[1] + (coldef,))
        }

    def _draw_prompt(self):
        x, y = 0, self.line
        prompt = self._prompt
        q, i = prompt["query"], prompt["input"]
        coldef = self.instance.color("Default")
        for ch, color in zip(q[0], q[1]):
            self.instance.set_cell(x, y, ch, color, coldef)
            x += 1
        x, y = 0, self.line + 1
        for ch, color in zip(i[0], i[1]):
            self.instance.set_cell(x, y, ch, color, coldef)
            x += 1
        return None

    def _draw_widget(self):
        w, h = self.WIDTH, 1
        self._adjust_voffset(w)
        t = self._text
        lx, tabstop = 0, 0
        coldef = self.instance.color("Default")
        x, y = len(self._prompt["input"]) + 1, self.line + 1
        while True:
            rx = lx - self._visual_offset
            if len(t) == 0:
                break
            if lx == tabstop:
                tabstop += self.TABSTOP
            if rx >= w:
                self.instance.set_cell(x+w-1, y, '→', coldef, coldef)
                break
            rune = t[0]
            if rune == '\t':
                while lx < tabstop:
                    rx = lx - self._visual_offset
                    if rx >= w:
                        break
                    if rx >= 0:
                        self.instance.set_cell(x+rx, y, ' ', coldef, coldef)
                    lx += 1
            else:
                if rx >= 0:
                    self.instance.set_cell(x+rx, y, rune, coldef, coldef)
                lx += self.instance.rune_width(rune)
            # next:
            t = t[len(rune):]

        if self._visual_offset != 0:
            self.instance.set_cell(x, y, '←', coldef, coldef)

    def _clear_all(self):
        coldef = self.instance.color("Default")
        self.instance.clear(coldef, coldef)

    def _redraw_all(self):
        self._clear_all()
        self._draw_prompt()
        self._draw_widget()
        x, y = len(self._prompt["input"]) + 1, self.line + 1
        self.instance.set_cursor(x+self._cursorX(), y)
        self.instance.flush()

    def _run(self):
        # check minimum width and height
        w, h = self.instance.size()
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
    def _draw_widget(self):
        w, h = self.WIDTH, 1
        self._adjust_voffset(w)
        t = self._text
        lx, tabstop = 0, 0
        coldef = self.instance.color("Default")
        x, y = len(self._prompt["input"]) + 1, self.line + 1
        while True:
            rx = lx - self._visual_offset
            if len(t) == 0:
                break
            if lx == tabstop:
                tabstop += self.TABSTOP
            if rx >= w:
                self.instance.set_cell(x+w-1, y, '→', coldef, coldef)
                break
            rune = "*"
            if rune == '\t':
                while lx < tabstop:
                    rx = lx - self._visual_offset
                    if rx >= w:
                        break
                    if rx >= 0:
                        self.instance.set_cell(x+rx, y, ' ', coldef, coldef)
                    lx += 1
            else:
                if rx >= 0:
                    self.instance.set_cell(x+rx, y, rune, coldef, coldef)
                lx += self.instance.rune_width(rune)
            # next:
            t = t[len(rune):]

        if self._visual_offset != 0:
            self.instance.set_cell(x, y, '←', coldef, coldef)
