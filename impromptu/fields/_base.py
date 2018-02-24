class Question(object):
    """The base Question type.

    A Question holds rendering configuration as well as
    validation, jump logic, function handlers, defaults,
    and other features.

    Text is rendered using a colormap which is a list of
    color triplets that describes the foreground (fg),
    attribute (attr), and background (bg) for each character
    in the string.

    The renderer takes a tuple. The first value is the text
    to be displayed. The second value is the colormap. The
    length of the text and the colormap must match. Type: (str, colormap)

    Attributes:
        instance (Impromptu): The "wrapper" Impromptu instance.
        widget (str): The Question component used.
        name (str): A name to use when storing the responses to each Question.
        query (str): The content of the question for prompting.
        default (str): The default answer. Defaults to "".
        result (str): The value of the response to the query.
        config (dict): Dict holding rendering details specific to each key.
        linenum (int): Logs the line number to which the Question is being rendered

    Note:
        Config keys include:
        * icon (tuple): The prefix added to each querystring. Default: [?], ? is Green.
        * query (tuple): The querystring. Configured on init.
        * prompt (tuple): Symbol for the start of a textbox. Default: », Red. (Text/Password only)

        * cursor (tuple): The symbol for selecting options in choice fields. Default: ›, Cyan. (Choice/Multi only)
        * selected (string): Symbol for a selected choice state. Default: ◉ (*nix) | ► (win) (Multi only)
        * unselected (string): Symbol for an open choice state. Default: ○ (Multi only)
        * inputs (triplet): Color for the user inputted text. (Text/Password only)
        * active (triplet): Color state for choice text when the cursor is on top of a choice. Default: Cyan. (Choice/Multi only)
        * inactive (triplet): Color state for choice text when the cursor is on NOT top of a choice. Default: Default/White. (Choice/Multi only)
        * height (int): Set the number of vertical space to occupy between Questions.

    Todo:
        * validators (list(str)): maybe some kind of list of regexes?
        * jump logic
        * loaders and spinners
        * function handlers (maybe to execute xyz based on response)
        * tooltips/help messages
        * autocomplete

    """

    def __init__(self, name, query, default="",
                 color=None, colormap=None):
        self.instance = None
        self.widget = None
        self.name = name
        self.query = query
        self.default = default
        self.result = ""
        self.config = {}
        self.linenum = 0
        if color is None:
            color = (0, 0, 0)
        if colormap is None:
            query_colormap = [color for _ in query]
        else:
            query_colormap = colormap
        self.config["height"] = 2
        self.config["icon"]   = ("[?]", [(0,0,0), (3,0,0), (0,0,0)])
        self.config["query"]  = (query, query_colormap)

    def _set_line(self, n):
        self.linenum = n
        return None

    def _draw_query(self):
        x, y = 0, self.linenum
        icon, query = self.config["icon"], self.config["query"]
        prompt = f"{icon[0]} {query[0]}"
        colormap = icon[1] + [(0,0,0)] + query[1] # [(0,0,0)] for the nbsp;
        for ch, colors in zip(prompt, colormap):
            fg, attr, bg = colors
            self.instance.set_cell(x, y, ch, fg|attr, bg)
            x += 1
        return None

    def _run(self):
        pass

    def setup(self):
        """Sets up the config attribute of the Question instance.

        Setup handles the config keys relevant to the Question type.
        Text/Password types will setup icon, prompt, and user input color.
        Single/MultiSelect types will configure cursor, active, selected,
        unselected, and custom colors for each specified choice.
        """
        pass

    def ask(self):
        self._draw_query()
        self._run()
        self.instance.clear(0, 0)
        return None
