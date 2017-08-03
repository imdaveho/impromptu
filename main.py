from impromptu.fields import TextInput, PasswordInput
import time


if __name__ == "__main__":
    ti = TextInput(name="name", query="What is your name?")
    err = ti.instance.init()
    if err:
        raise(Exception(err))
    ti.instance.set_input_mode(ti.instance.input("Esc"))
    pi = PasswordInput(name="password", query="Password:")
    qs = [ti, pi]
    for i, x in enumerate(qs):
        x.set_line(i * x.height + 1)
        x.ask()
    ti.instance.close()
    # print(ti.name)
    # print(ti.query)
    # print(ti.result)
    # print("=================================")
    # print(pi.name)
    # print(pi.query)
    # print(pi.result)
