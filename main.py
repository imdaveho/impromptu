from impromptu.fields import TextInput
import time


if __name__ == "__main__":
    ti = TextInput(name='name', query='What is your name?')
    err = ti.instance.init()
    if err:
        raise(Exception(err))
    ti.instance.set_input_mode(ti.instance.input("Esc"))
    ti._draw_query()
    ti._draw_prompt()
    ti.instance.flush()
    time.sleep(2)
    ti.instance.close()
