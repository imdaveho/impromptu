from impromptu import Impromptu
from impromptu import fields


def validation(obj, index):
    # right now, the user must specify these params for mutex handling
    # TODO: make a wrapper that simply allows the user to pass in a normally
    # constructed function and have the API handle the mutex-ing
    mzo = obj.cli
    w, h = mzo.size()
    error_msg = "Error: This is an invalid answer"
    if obj._text == "hello":
        obj.evt_mutex = index
    # error_msg = f"Value: {obj._text}"
    # if True:
        for i in range(w):
            mzo.set_cell(i, h-3, "_", mzo.color("Red"), 0)
        for i, c in enumerate(error_msg):
            mzo.set_cell(i, h-2, c, mzo.color("Red"), 0)
        mzo.flush()
        evts = obj.pull_events()
        if not evts:
            return
        evt = evts[0]
        if evt["Type"] == obj.cli.event("Key") \
           and obj.evt_mutex == index:
            k, c = evt["Key"], evt["Ch"]
            if k == obj.cli.key("Esc"):
                obj.evt_mutex = -1
                for i in range(h-3, h):
                    y = i
                    for x in range(w):
                        obj.cli.set_cell(x, y, " ", 0, 0)


if __name__ == "__main__":
    instance = Impromptu()
    q1 = fields.TextInput(name="name", query="What is your name?")
    instance.register(q1)
    q1.on_update(validation)
    instance.start()

# if __name__ == "__main__":
#     instance = Impromptu()
#     q1 = TextInput(name="name", query="What is your name?")
#     q2 = PasswordInput(name="email", query="What is your email?")
#     q2.setup(icon="<?>", prompt=(">>>>>>>", (6,0,0)))
#     instance.register(q1)
#     instance.register(q2)
#     q3 = MultiSelect(name="favorite", query="What is your favorite food?",
#                      choices=["Pizza", "Steak", "Spaghetti", "Fried Chicken", "Kale", "Burgers", "Lobster", "Ice Cream"])
#     q3.setup(posthook={
#         "Lobster": False
#     })
#     instance.register(q3)
#     instance.start()

# if __name__ == "__main__":
#     instance = Impromptu()
#     sym = {
#         "icon": "[?]",
#     }
#     col = {
#         "icon": (0, mzo.color("Blue"), 0),
#     }

#     q1 = TextInput(name="name", query="What is your name?", symbols=sym, colors=col)
#     # q2 = ChoiceSelect(name="favorite", query="What is your favorite food?",
#     #                   choices=["Pizza", "Burgers", "Sushi", "BBQ",
#     #                            "Pancakes", "Salad", "Ice Cream",
#     #                            "Yogurt", "Bagels", "Fish"])
#     q2 = MultiSelect(name="favorite", query="What is your favorite food?",
#                       choices=["Pizza", "Burgers", "Sushi", "BBQ",
#                                "Pancakes", "Salad", "Ice Cream",
#                                "Yogurt", "Bagels", "Fish"])
#     instance.add(q1)
#     instance.add(q2)
#     instance.ask()


# from impromptu.fields import TextInput, PasswordInput
# import time


# if __name__ == "__main__":
#     ti = TextInput(name="name", query="What is your name?")
#     err = ti.instance.init()
#     if err:
#         raise(Exception(err))
#     ti.instance.set_input_mode(ti.instance.input("Esc"))
#     pi = PasswordInput(name="password", query="Password:")
#     qs = [ti, pi]
#     for i, x in enumerate(qs):
#         x.set_line(i * x.height + 1)
#         x.ask()
#     ti.instance.close()
#     # print(ti.name)
#     # print(ti.query)
#     # print(ti.result)
#     # print("=================================")
#     # print(pi.name)
#     # print(pi.query)
#     # print(pi.result)
