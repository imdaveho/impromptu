from intermezzo import Intermezzo as mzo

class Impromptu(object):
    """The main rendering engine for Questions.

    Attributes:
        index (int): The current index of the Question being asked.
        questions (list(Question)): The internal collection of Questions.

    """

    def __init__(self):
        self.questions = []
        self.responses = {}

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

    def should_mount(self, index, question):
        mount = "prehook"
        default = question.on(mount, "__default__")
        default_action = default["action"]
        if default_action:
            default_action()
        lookups = []
        if index > 0:
            question = self.questions[index - 1]
        result = question.result
        if type(result) is list:
            lookups = result
        else:
            lookups.append(result)
        renders = []
        for lookup in lookups:
            hook = question.on(mount, lookup)
            render = hook["valid"]
            hook_action = hook["action"]
            if hook_action:
                render = hook_action()
            renders.append(render)
        # TODO: error handling
        should_render = any(renders)
        return should_render

    def should_proceed(self, question):
        unmount = "posthook"
        default = question.on(unmount, "__default__")
        default_action = default["action"]
        if default_action:
            default_action()
        lookups = []
        result = question.result
        if type(result) is list:
            lookups = result
        else:
            lookups.append(result)
        errors = []
        for lookup in lookups:
            hook = question.on(unmount, lookup)
            is_valid = hook["valid"]
            if not is_valid:
                error = hook["error"]
                errors.append(error)
        return errors

    def start(self):
        """
        Executes the main method of each of the Questions in the internal
        collection and renders their contents to the screen
        """
        i = 0
        # for q in self.questions:
        while len(self.questions) > i:
            q = self.questions[i]
            should_mount = self.should_mount(i,q)
            if should_mount:
                q.ask()
            errors = self.should_proceed(q)
            if any(errors):
                # x = 0
                # y = q.linenum + q.size + 2
                # for e in errors:
                #     # TODO: display errors
                #     for ch in e:
                #         fg, attr, bg = 7, 0, 0
                #         mzo.set_cell(x, y, ch, fg|attr, bg)
                #         x += 1
                #     q._redraw_all()
                #     pass
                # # TODO: re-run this question
                # #       continue will skip i++
                # # TODO: reset question!
                # from time import sleep
                # sleep(1)
                continue
                # TODO: should re-run __default__?
            i += 1
        results = {}
        mzo.close()
        for q in self.questions:
            results[q.name] = q.result
        self.responses = results
        print(self.responses)
