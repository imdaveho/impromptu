from intermezzo import Intermezzo as mzo
from impromptu.utils.registrar import Registrar


class Impromptu(object):
    """The main rendering engine for Questions.

    Attributes:
        index (int): The current index of the Question being asked.
        questions (list(Question)): The internal collection of Questions.

    """

    def __init__(self):
        self.responses = {}
        self.registrar = Registrar()

    def register(self, question):
        """
        Append Questions to the internal Question registry

        Args:
            question (Question): Adds the question to the internal collection.
        """
        self.registrar.put(question)

    def prompt(self, cli, registrar):
        while True:
            # prepare query variables
            query = registrar.get()
            if query is None:
                break
            query.cli = cli
            query.registrar = registrar
            # handle query lifecycle
            should_mount = query.mount()
            if should_mount is not False:
                query.clear_below()
                query.ask()
                did_unmount = query.unmount()
                if did_unmount is False:
                    query.reset()
                    query.restart()
                else:
                    query.close()
            else:
                query.close()

    def start(self):
        """
        TODO: ...
        """
        # initialize Intermezzo
        err = mzo.init()
        if err:
            raise(Exception(err))
        # TODO: set mzo settings on init
        mzo.set_input_mode(mzo.input("Esc"))
        mzo.set_output_mode(mzo.output("256"))

        try:
            self.prompt(mzo, self.registrar)
        finally:
            mzo.close()
            for o in self.registrar.registry.values():
                q = o["data"]
                self.responses[q.name] = q.result
