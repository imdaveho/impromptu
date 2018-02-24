from intermezzo import Intermezzo as mzo

class Impromptu(object):
    """The main rendering engine for Questions.

    Attributes:
        index (int): The current index of the Question being asked.
        questions (list(Question)): The internal collection of Questions.

    """

    def __init__(self):
        self.index = 0
        self.questions = []

        # initialize Intermezzo
        err = mzo.init()
        if err:
            raise(Exception(err))
        # TODO: set mzo settings on init
        mzo.set_input_mode(mzo.input("Esc"))
        mzo.set_output_mode(mzo.output("256"))

    def register(self, question):
        """
        Append Questions to the internal collection and references the Intermezzo
        instance that was initialized upon starting the Impromptu instance.

        Args:
            question (Question): Adds the question into the internal collection.
        """
        question.instance = mzo
        self.questions.append(question)

    def start(self):
        """
        Executes the main method of each of the Questions in the internal
        collection and renders their contents to the screen
        """
        for q in self.questions:
            q.ask()
        results = {}
        mzo.close()
        for q in self.questions:
            results[q.name] = q.result
        print(results)
