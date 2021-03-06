import threading
from functools import wraps
from functools import partial
from collections import deque
from intermezzo import Intermezzo as mzo
from impromptu.utils.multimethod import configure


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
        linenum (int): The line number to which the Question is being rendered

    Note:
        Config keys include:
        * icon (tuple): The prefix added to each querystring. Default: [?],
    ? is Green.
        * query (tuple): The querystring. Configured on init.
        * prompt (tuple): Symbol for the start of a textbox. Default: », Red.
    (Text/Password only)

        * cursor (tuple): The symbol for selecting options in choice fields.
    Default: ›, Cyan. (Choice/Multi only)
        * selected (string): Symbol for a selected choice state.
    Default: ◉ (*nix) | ► (win) (Multi only)
        * unselected (string): Symbol for an open choice state. Default: ○
    (Multi only)
        * inputs (triplet): Color for the user inputted text.
    (Text/Password only)
        * active (triplet): Color state for choice text when the cursor is on
    top of a choice. Default: Cyan. (Choice/Multi only)
        * inactive (triplet): Color state for choice text when the cursor is
    on NOT top of a choice. Default: Default/White. (Choice/Multi only)
        * linespace (int): Set the number of vertical space to occupy between
    Questions.

    Todo:
        * loaders and spinners
        * tooltips/help messages
        * autocomplete

    """

    def __init__(self, name, query, default="",
                 color=None, colormap=None):
        self._threads = []
        self._keys_in_use = []
        # set variables sent through initialization
        self.name = name
        self.query = query
        self.default = default
        if color is None:
            color = (0, 0, 0)
        if colormap is None:
            query_colormap = [color for _ in query]
        else:
            query_colormap = colormap
        # set variables pass through the main prompt loop
        self.cli = None
        self.loop = None
        self.registrar = None
        # set configuration variables
        self.widget = ""
        self.result = ""
        self.linenum = 0
        self.config = {}
        self.config["linespace"] = 2
        self.config["icon"] = ("[?]", [(0, 0, 0), (3, 0, 0), (0, 0, 0)])
        self.config["query"] = (query, query_colormap)
        self.config["refresh"] = False
        self.config["result"] = (4, 0, 0)
        self.lifecycle = {}
        self.lifecycle["mount"] = None
        self.lifecycle["unmount"] = None
        self.lifecycle["updates"] = {}
        self.lifecycle["validations"] = {}
        self.evt_mutex = True
        self.evt_stream = deque(maxlen=20)
        self.end_signal = False

    def _partial(self, f):
        # TODO: update to account for self-less functions passed in or
        # situations where self may not be the first argument in the list...
        # https://stackoverflow.com/questions/42352703/get-names-of-positional-arguments-from-functions-signature
        if f is None or not callable(f):
            return True
        if isinstance(f, partial):
            try:
                f = partial(f.func, self, *f.args, **f.keywords)
            except Exception as e:
                return True
        return f

    def _poll_event(self):
        e = self.cli.poll_event()
        self.evt_stream.append(e)

    def _clean_threads(self):
        is_alive = [t for t in self._threads if t.is_alive()]
        for t in is_alive:
            t.join()
        self._threads = []

    def mount(self):
        """Use to set up everything necessary for the Question.

        Examples:
          - check if file exists, if not download it
          - see if API token is still valid, if not refresh it

        Pass through self so that the function has access to Intermezzo

        or

        Use to dynamically update the parameters for render.

        Examples:
          - based on previous response, update the options for a MultiSelect
          - read from a file for autocomplete options or regex for a TextInput

        Pass through self so that the function has access to the Registry
        """
        f = self._partial(self.lifecycle["mount"])
        if isinstance(f, partial) and callable(f.func):
            return f()
        return f

    def unmount(self):
        """Use to perform clean up and logic jumps.

        Examples:
          - delete temporary files downloaded from before
          - update the Question flow based on the response

        Pass through self to that the function has access to the Registry
        """
        f = self._partial(self.lifecycle["unmount"])
        if isinstance(f, partial) and callable(f.func):
            return f()
        return f

    def close(self):
        # render with result
        x, y = 0, self.linenum
        icon, query = self.config["icon"], self.config["query"]
        result = self.result
        if type(result) is list:
            count = len(result)
            result = f"[{count}] items"
        if self.widget == "password":
            count = len(result)
            result = "".join(["*" for _ in range(count)])
        result_cm = [self.config["result"] for _ in result]
        prompt = f"{icon[0]} {query[0]}  {result}"
        colormap = icon[1] + [(0, 0, 0)] + query[1]  # [(0,0,0)] for the nbsp;
        colormap = colormap + [(0, 0, 0,), (0, 0, 0)] + result_cm
        for ch, colors in zip(prompt, colormap):
            fg, attr, bg = colors
            self.cli.set_cell(x, y, ch, fg | attr, bg)
            x += 1
        # update line spacing of next question
        nq_key = self.registrar.subsequent()
        if nq_key:
            nq = self.registrar.registry[nq_key]["data"]
            if self.config["refresh"]:
                nq.linenum = 0
                self.cli.clear(0, 0)
            else:
                nq.linenum = self.config["linespace"] + self.linenum
                w, h = self.cli.size()
                for y in range(self.linenum + 1, h + 1):
                    for x in range(w):
                        self.cli.set_cell(x, y, " ", 0, 0)

    def render(self):
        x, y = 0, self.linenum
        icon, query = self.config["icon"], self.config["query"]
        prompt = f"{icon[0]} {query[0]}"
        colormap = icon[1] + [(0, 0, 0)] + query[1]  # [(0,0,0)] for the nbsp;
        for ch, colors in zip(prompt, colormap):
            fg, attr, bg = colors
            self.cli.set_cell(x, y, ch, fg | attr, bg)
            x += 1

    def redraw_all(self):
        """Updates the render loop to account for any changes to the Widget"""
        pass

    def reset(self):
        self.result = ""
        self.end_signal = False

    def restart(self):
        self.registrar.cursor = self.registrar.running
        self.end_signal = False

    def setup(self, **kwargs):
        """Sets up the config attribute of the Question instance.

        Setup handles the config keys relevant to the Question type.
        Text/Password types will setup icon, prompt, and user input color.
        Single/MultiSelect types will configure cursor, active, selected,
        unselected, and custom colors for each specified choice.
        """
        for k, v in kwargs.items():
            args = self._set_config(k, v)
            if not v or args is None:
                # skip the parameters that have not been passed
                # for some reason, if _set_config returns None
                continue
            self.config[k] = configure(*args)
        return self

    def on_mount(self, fn, *args, **kwargs):
        if callable(fn):
            self.lifecycle["mount"] = partial(fn, *args, **kwargs)

    def on_unmount(self, fn, *args, **kwargs):
        if callable(fn):
            self.lifecycle["unmount"] = partial(fn, *args, *kwargs)

    def clear_below(self):
        w, h = self.cli.size()
        for i in range(h):
            y = i + self.linenum + 1
            for x in range(w):
                self.cli.set_cell(x, y, " ", 0, 0)
        self.cli.flush()

    def _main(self):
        """Execute the main processes for the field at hand.

        Each widget/field will be implemented differently
        """
        while True:
            if self.end_signal:
                break
            if self.evt_mutex:
                self._handle_validations()
                self._poll_event()
                self._handle_events()
                self._handle_updates()
                self.redraw_all()
        self._clean_threads()

    def _handle_updates(self):
        e = self.pull_events()[0]
        if e["Type"] == self.cli.event("Key"):
            fn = self.lifecycle["updates"].get(e["Key"], None)
            if fn:
                t = threading.Thread(target=fn)
                self._threads.append(t)
                t.start()

    def _handle_validations(self):
        pass

    def pull_events(self, cache=5):
        """Handler that returns the last cached key events from the deque.

        Primarily to separate the event stream from usage of the event stream.
        By returning the values from the latest event stream, each function
        that might need events can operate without fear of mutation. Only grab
        the latest cached events up to the last 20.
        """
        evts = self.evt_stream.copy()
        length = len(evts)
        if length == 0:
            return [{"Type": 7}]
        if length < cache:
            evt_log = [evts.pop() for _ in range(length)]
        elif length >= 20:
            evt_log = [evts.pop() for _ in range(20)]
        else:
            evt_log = [evts.pop() for _ in range(cache)]
        return evt_log

    def _is_update_valid(self, key):
        if key in self.lifecycle["updates"].keys():
            return False
        if key in self._keys_in_use:
            return False
        return True

    def update(self, k):
        def wrapper(self, fn):
            @wraps(fn)
            def register(k):
                if not self._is_update_valid(k):
                    raise Exception("This update key is already in use.")
                if mzo.key(k) is None:
                    raise Exception("This update key is not valid " +
                                    "or is unsupported.")
                self.lifecycle["updates"][mzo.key(k)] = partial(fn, self)
            register(k)
        return partial(wrapper, self)

    def ask(self):
        self.render()
        self.redraw_all()
        self._main()
