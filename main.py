import time
import intermezzo
from impromptu import Impromptu
from impromptu import fields


q1 = fields.PasswordInput(name="name", query="What is your name?")


# @q1.update("CtrlT")
@q1.validate(r"(^[A-Z])|(_)|(-)|\s")
def validation(self):
    mzo = self.cli
    w, h = mzo.size()
    error_msg = f"Error: This is an invalid answer | {len(self._threads)}"
    for i in range(w):
        mzo.set_cell(i, h-3, "_", mzo.color("Red"), 0)
    for i, c in enumerate(error_msg):
        mzo.set_cell(i, h-2, c, mzo.color("Red"), 0)
    mzo.flush()
    # sched()
    time.sleep(1)
    for i in range(h-3, h):
        y = i
        for x in range(w):
            mzo.set_cell(x, y, " ", 0, 0)
    mzo.flush()


def logic_jump(obj):
    r = obj.registrar
    qs = {
        "Food": q3a,
        "Colors": q3b,
        "Cities": q3c,
        "Other": q3d
    }
    if obj.result == "Colors":
        return False
    else:
        r.insert(qs.get(obj.result))


if __name__ == "__main__":
    instance = Impromptu()
    q1.on_mount(lambda _: False)
    q2 = fields.ChoiceSelect(name="favorite", query="Pick a topic:",
                             choices=["Food", "Colors", "Cities"])
    q2.on_unmount(logic_jump)

    q3a = fields.MultiSelect(name="favorite_food",
                             query="What are your favorite foods?",
                             choices=["Pizza", "Steak", "Spaghetti",
                                      "Fried Chicken", "Kale", "Burgers",
                                      "Lobster", "Ice Cream"])
    q3a.setup(refresh=True)
    q3a.setup(linespace=6)

    q3b = fields.MultiSelect(name="favorite_color",
                             query="What are your favorite colors?",
                             choices=["Blue", "Red", "Green",
                                      "Purple", "Orange", "Yellow",
                                      "Pink", "Brown"])

    q3c = fields.MultiSelect(name="favorite_cities",
                             query="What are your favorite cities?",
                             choices=["NYC", "LA"])
                             # choices=["Boston", "Philly", "New York",
                             #          "LA", "San Francisco", "Hoboken",
                             #          "Houston", "Chicago"])

    q3d = fields.TextInput(name="favorite_other",
                           query="What other thing is your favorite?")

    questions = [q1, q2]
    for q in questions:
        instance.register(q)
    instance.start()
