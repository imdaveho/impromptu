from . import Question
from intermezzo import Intermezzo as mzo


class TextInput(Question):
    def __init__(self, name, query, config=None):
        super().__init__(name, query, config)
        self.TABSTOP = 8
        self.PADDING = 5
        self.WIDTH = 30
        self.widget = "text"
        self.height = 2
        self.text = ""
        self._visual_offset = 0
        self._cursor_offset = 0
        self._cursor_unicode_offset = 0

    def _render_text(self, x, y, fg, bg, msg):
        for c in msg:
            self.instance.set_cell(x, y, c, fg, bg)
            x += self.instance.rune_width(c)

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
        text = self.text[:coffset]
        voffset = 0
        while len(text) > 0:
            rune = text[0]
            text = text[len(rune):]
            voffset += self._rune_advance(rune, voffset)
        self._cursor_offset = voffset
        self._cursor_unicode_offset = coffset

    def _under_cursor(self):
        return self.text[self._cursor_unicode_offset]

    def _before_cursor(self):
        return self.text[self._cursor_unicode_offset - 1]

    def _move_one_backward(self):
        if self._cursor_unicode_offset == 0:
            return
        size = len(self._before_cursor())
        self._move_to(self._cursor_unicode_offset - size)

    def _move_one_forward(self):
        if self._cursor_unicode_offset == len(self.text):
            return
        size = len(self._under_cursor())
        self._move_to(self._cursor_unicode_offset + size)

    def _move_to_beginning(self):
        self._move_to(0)

    def _move_to_end(self):
        self._move_to(len(self.text))

    def _delete_backward(self):
        if self._cursor_unicode_offset == 0:
            return
        self._move_one_backward()
        size = len(self._under_cursor())
        self.text = self._remove(self.text, self._cursor_unicode_offset, self._cursor_unicode_offset + size)

    def _delete_forward(self):
        if self._cursor_unicode_offset == len(self.text):
            return
        size = len(self._under_cursor())
        self.text = self._remove(self.text, self._cursor_unicode_offset, self._cursor_unicode_offset + size)

    def _delete_to_end(self):
        self.text = self.text[:self._cursor_unicode_offset]

    def _insert_rune(self, rune):
        self.text = self._insert(self.text, self._cursor_unicode_offset, rune)
        self._move_one_forward()

    def _cursorX(self):
        return self._cursor_offset - self._visual_offset

    def _draw_query(self, colors=None):
        x = 0
        y = self.line
        query = self.template["query"] + ' ' + self.query
        coldef = self.instance.color("Default")
        if colors:
            query_colors = colors
        else:
            query_colors = [coldef for _ in query]
            query_colors[query.find('?')] = self.instance.color("Green")
        for i, ch in enumerate(query):
            color = query_colors[i]
            self.instance.set_cell(x, y, ch, color, coldef)
            x += 1
        return None

    def _draw_prompt(self, colors=None):
        x = 0
        y = self.line + 1
        prompt = self.template["prompt"]
        coldef = self.instance.color("Default")
        if colors:
            prompt_colors = colors
        else:
            prompt_colors = [coldef for _ in prompt]
            prompt_colors[prompt.find('»')] = self.instance.color("Red")
        for i, ch in enumerate(prompt):
            color = prompt_colors[i]
            self.instance.set_cell(x, y, ch, color, coldef)
            x += 1
        return None

    def _draw_widget(self, x, y):
        coldef = self.instance.color("Default")
        w, h = self.WIDTH, 1
        t = self.text
        lx = len(self.template['prompt'])
        tabstop = lx
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

    def _display(self):
        x, y = len(self.template['prompt']), self.line + 1
        self._draw_query()
        self._draw_prompt()
        self._draw_widget(x, y)
        self.instance.set_cursor(x+self._cursorX(), y)
        self.instance.flush()

    def _run(self):
        coldef = self.instance.color("Default")
        self.instance.clear(coldef, coldef)
        # check minimum width and height
        w, h = self.instance.size()
        # do the check here:

        # draw the query and prompt
        self._display()
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
            self._display()
        # set the correct height now???
        self.line = self.height
