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
        self.registrar.put(question)

    async def prompt(self, cli, loop, registrar):
        while True:
            # prepare query variables
            query = registrar.get()
            if query is None:
                break
            query.cli = cli
            query.loop = loop
            query.registrar = registrar  # TODO: rename please
            # handle query lifecycle
            should_mount = query.mount()
            if should_mount:
                await query.ask()
                did_unmount = query.unmount()
                if did_unmount is False:
                    query.reset()
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
            results = []
            for q in self.registrar.registry.values():
                results.append(q.get("data").result)
            print(results)
