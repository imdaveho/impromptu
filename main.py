from intermezzo import Intermezzo as mzo
from impromptu.fields import *

if __name__ == "__main__":
    instance = Impromptu()
    # q1 = TextInput(name="name", query="What is your name?", settings={"query_icon":("[?]", (0, mzo.color("Blue"), 0))})
    q1 = ChoiceSelect(name="favorite", query="What is your favorite food?",
                      choices=["Pizza", "Burgers", "Sushi", "BBQ",
                               "Pancakes", "Salad", "Ice Cream",
                               "Yogurt", "Bagels", "Fish"])
    instance.add(q1)
    instance.ask()


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
