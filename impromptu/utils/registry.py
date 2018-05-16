"""A helper class to manage the logical flow of Questions.

"""
import time
import random

class Registrar(object):

    def __init__(self):
        self.registry = {}
        self.orphaned = {}
        self.branched = {}
        self.entry = None
        self.cursor = None
        self.running = None

    def _make_unique_key(self):
        keys = list(self.registry.keys())
        timestamp = None
        # ensure the inserted key is unique
        while True:
            timestamp = int(time.strftime("%m%d%H%M%S"))
            key = random.randint(0, timestamp)
            if not key in keys:
                return key

    def put(self, question):
        unique_key = self._make_unique_key()
        # link the questions together by referencing their unique keys
        previous_key = None
        if not keys:
            self.entry = unique_key
            self.cursor = unique_key
        else:
            previous_key = keys[-1]
            self.registry[previous_key]["next"] = unique_key
        # append to the registry
        self.registry[unique_key] = {
            "data": question,
            "key": unique_key,
            "prev": previous_key,
            "next": None
        }
        return unique_key

    def get(self):
        # grabs the question of the current cursor
        # moves the cursor to the next question
        question = self.registry[self.cursor]["data"]
        self.running = self.cursor
        self.cursor = self.registry[self.cursor]["next"]
        return question

    def current(self):
        return self.registry[self.running]

    def previous(self):
        return self.registry[self.running]["prev"]

    def subsequent(self):
        return self.registry[self.running]["next"]

    def insert(self, *questions):
        if not questions:
            questions = []
        subsequent = self.subsequent()
        running = self.current()
        previous = None
        for i, q in enumerate(questions):
            unique_key = self._make_unique_key()
            this_question = {
                "data": q,
                "key": unique_key,
                "prev": None,
                "next": None
            }
            if i == 0:
                # this is the first question inserted
                # update self.cursor to this unique key so that
                # running self.get() will result in this question
                # instead of the previous subsequent question
                # the prev of this question is the running question
                # the next is the next question in the list, which
                # will get resolved in the next loop
                self.cursor = unique_key
                running["next"] = unique_key
                this_question["prev"] = running["key"]
            elif i == len(questions) - 1:
                # this is the last question to be inserted
                # the prev is the previous question's key
                # the next was the previously subsequent question
                subsequent["prev"] = unique_key
                this_question["prev"] = previous["key"]
                this_question["next"] = subsequent["key"]
            else:
                # this is a question between the first and last
                # this question's prev is the previous question's key
                # this also resolves the previous question's next
                # this question's next will be resolved in the next loop
                previous["next"] = unique_key
                this_question["prev"] = previous["key"]
            # this inserts it into the registry
            self.registry[unique_key] = this_question
            # update the variable that points to this dict so that in the
            # next loop the next key can be resolved
            previous = this_question

    def _list_linked_keys(self):
        linked_key = None
        linked_keys = []
        subsequent = self.subsequent()
        while True:
            if not linked_keys:
                linked_key = subsequent["key"]
            else:
                linked_key = self.registry[linked_key]["next"]
            if not linked_key:
                break
            linked_keys.append(linked_key)
        return linked_keys

    def branch(self, *questions):
        if not questions:
            questions = []
        running = self.current()
        previous = None
        for i, q in enumerate(questions):
            unique_key = self._make_unique_key()
            this_question = {
                "data": q,
                "key": unique_key,
                "prev": None,
                "next": None,
                "origin": running["key"]
            }
            if i == 0:
                # this is the first question that diverges
                # update self.cursor to this unique key so that
                # running self.get() will result in this question
                # instead of the upcoming question that was branched
                # the prev of this question is the running question
                # the next is the next question in the list, which
                # will get resolved in the next loop
                self.cursor = unique_key
                running["next"] = unique_key
                this_question["prev"] = running["key"]
                # update self.branched with the key of the question
                # that the branch originated from
                branched_keys = self._list_linked_keys()
                self.branched[running["key"]] = branched_keys
            else:
                # this question's prev is the previous question's key
                # this also resolves the previous question's next
                # this question's next will be resolved in the next loop
                previous["next"] = unique_key
                this_question["prev"] = previous["key"]
            # this inserts it into the registry
            self.registry[unique_key] = this_question
            # update the variable that points to this dict so that in the
            # next loop the next key can be resolved
            previous = this_question

    def merge(self, key=None):
        running = self.current()
        origin = running.get("origin", False)
        if not origin:
            # TODO: refine error messaging
            raise Exception("No branches found!")
        valid_keys = self.branched[origin]
        if not key:
            key = valid_keys[0]
        if key in valid_keys:
            # if merged back, but not to the start of the branch,
            # any questions skipped over will be orphaned by the
            # branch origin; record it:
            key_index = valid_keys.index(key)
            orphaned_keys = valid_keys[:key_index]
            for orphan in orphaned_keys:
                self.orphaned[orphan] = origin
            # if merged back without finishing the remaining
            # branched questions, if any, the remaining will
            # effectively be orphaned; note this:
            merging = self.registry[key]
            orphaned_keys = self._list_linked_keys()
            for orphan in orphaned_keys:
                self.orphaned[orphan] = running["key"]
            # update links between questions
            running["next"] = key
            merging["prev"] = running["key"]
            # update the cursor
            self.cursor = key
        else:
            # TODO: refine error messaging
            raise Exception("Not a valid merge candidate!")


    def skip(self, key=None):
        # needs to update self.orphans
        running = self.current()
        valid_keys = self._list_linked_keys()
        if not key:
            # if a key isn't provided, skip over one question
            key = valid_keys[1]
            orphan = valid_keys[0]
            self.orphaned[orphan] = running["key"]
        else:
            if key not in valid_keys:
                # TODO: refine error messaging
                raise Exception("Invalid skip target!")
            key_index = valid_keys.index(key)
            orphaned_keys = valid_keys[:key_index]
            for orphan in orphaned_keys:
                self.orphaned[orphan] = running["key"]
        new_next = self.registry[key]
        running["next"] = new_next
        new_next["prev"] = running["key"]
        self.cursor = new_next
