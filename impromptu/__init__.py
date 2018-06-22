import asyncio
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
        # question.instance = mzo
        # question.registrar = self.registrar
        # question.eventloop = loop
        self.registrar.put(question)

    async def prompt(self, cli, loop, registry):
        while True:
            query = registry.get()
            if query is None:
                break
            query.cli = cli
            query.loop = loop
            query.registry = registry
            await query.ask()

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

        # start the event loop
        evt_loop = asyncio.get_event_loop()
        try:
            evt_loop.run_until_complete(self.prompt(
                mzo, evt_loop, self.registrar
            ))
        finally:
            mzo.close()
            evt_loop.close()
            # TODO: loop through the registry and print results
