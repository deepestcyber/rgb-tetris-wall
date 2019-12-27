import threading
import time


def r():
    fn = "wator.py"
    with open(fn, 'r') as f:
        code = compile(f.read(), fn, "exec")
    exec(code)


t = threading.Thread(target=r, daemon=True)

t.start()
time.sleep(4)
