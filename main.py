from impromptu import Impromptu
from impromptu import fields


def validation(obj):
    # right now, the user must specify these params for mutex handling
    # TODO: make a wrapper that simply allows the user to pass in a normally
    # constructed function and have the API handle the mutex-ing
    mzo = obj.cli
    w, h = mzo.size()
    error_msg = "Error: This is an invalid answer"
    if obj._text == "hello":
        obj.evt_mutex = 998
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
           and obj.evt_mutex == 998:
            k, c = evt["Key"], evt["Ch"]
            if k == obj.cli.key("Esc"):
                obj.evt_mutex = -1
                for i in range(h-3, h):
                    y = i
                    for x in range(w):
                        obj.cli.set_cell(x, y, " ", 0, 0)


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
    q1 = fields.PasswordInput(name="name", query="What is your name?")
    # q1.on_mount(lambda _: False)
    q1.on_update(validation)
    q1.setup(refresh=True)

    q2 = fields.ChoiceSelect(name="favorite", query="Pick a topic:",
                             choices=["Food", "Colors", "Cities"])
                             # choices=["Food", "Colors", "Cities", "Other"])

    q2.on_unmount(logic_jump)
    q2.setup(result=6)

    q3a = fields.MultiSelect(name="favorite_food",
                             query="What are your favorite foods?",
                             choices=["Pizza", "Steak", "Spaghetti",
                                      "Fried Chicken", "Kale", "Burgers",
                                      "Lobster", "Ice Cream"])
    # q3a.setup(reset_view=True)
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

    m = "Qui ab distinctio voluptatum eveniet aut assumenda temporibus. Error maxime quo enim commodi ex dolores velit laboriosam. Facere eaque magnam magnam. Ipsam ea ut rem distinctio nihil commodi. Placeat fuga corporis corrupti qui officiis excepturi et qui. Nemo voluptatem est asperiores sed.…"
    q4 = fields.StaticMessage(name="msg", query="A word from our sponsor:",
                              message=m)

    # questions = [q1, q1]
    questions = [q1, q2, q4]
    # questions = [q1, q2]
    for q in questions:
        instance.register(q)
    instance.start()

    # for e in instance.registrar.registry.values():
    #     print(e)

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
