from ._base import Question


class StaticMessage(Question):
    def __init__(self, name, query, message="", default="",
                 width=120, color=None, colormap=None):
        super().__init__(name, query, default, color, colormap)
        self._keys_in_use = ["Enter"]
        self.widget = "static"
        self.message = message
        self.config["icon"] = ("[!]", [(0, 0, 0), (4, 0, 0), (0, 0, 0)])
        self.config["prompt"] = (" » ", [(0, 0, 0), (4, 0, 0), (0, 0, 0)])
        self.config["width"] = width
        self.config["message"] = (4, 0, 0)
        if color is None:
            color = (4, 0, 0)
        if colormap is None:
            query_colormap = [color for _ in query]
        else:
            query_colormap = colormap
        self.config["query"] = (query, query_colormap)

    def _set_config(self, n, c):
        default = self.config[n]
        return {
            "icon": (*c, default) if type(c) is tuple else (c, default),
            "prompt": (*c, default) if type(c) is tuple else (c, default),
            "height": (c, default),
            "inputs": (c, default),
            "refresh": (c, default),
        }.get(n, None)

    def setup(self, icon=False, prompt=False, message=False,
              width=False, refresh=False):
        kwargs = {
            "icon": icon,
            "prompt": prompt,
            "width": width,
            "message": message,
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

    def _draw_message(self):
        x = len(self.config["prompt"][0]) + 1
        y = self.linenum + 1
        w = self.config["width"]
        length = len(self.message)
        segments = []
        for i in range(0, length, w):
            segment = self.message[i:i+w]
            segments.append(
                (segment, [self.config["message"] for _ in segment]))
        for dy, s in enumerate(segments):
            segment, colormap = s
            dx = 0
            for ch, colors in zip(segment, colormap):
                fg, attr, bg = colors
                self.cli.set_cell(x + dx, y + dy, ch, fg | attr, bg)
                dx += 1
        return None

    def redraw_all(self):
        self.cli.hide_cursor()
        self._draw_prompt()
        self._draw_message()
        self.cli.flush()

    def _handle_events(self):
        evt = self.pull_events()[0]
        if evt["Type"] == self.cli.event("Key"):
            k = evt["Key"]
            if k == self.cli.key("Enter"):
                self.end_signal = True
        elif evt["Type"] == self.cli.event("Error"):
            # EventError
            raise(Exception(evt["Err"]))
        return None
