from pynput.keyboard import KeyCode, Listener, Controller, Key as k
import time

keyb = Controller()

key = ""
key2 = ""

presses = []

abbreviations = {

}

key_list = {

}

hotkeys = {

}


def write(sentence):
    keyb.type(sentence)


key_presses = []

for op in range(100):
    presses.append(".")


row = 0

v = []


def on_press(Key):
    global key, presses, abbreviations, row, key2
    for oo in hotkeys.keys():
        print(hotkeys[oo])
        if Key == KeyCode(char=oo):
            if hotkeys[oo][1] == "":
                hotkeys[oo][0]()
            else:
                print(hotkeys[oo][1])
            break

    key = Key
    key2 = ""
    presses.append(Key)

    for ab in abbreviations.keys():
        row = 0
        g = 0
        res = []
        for nnn in ab:
            g += 1
            res.insert(0, presses[len(presses) - g])

        z = []

        for t in ab:
            z.append(KeyCode(char=t))

        if str(res) == str(z):
            for dfg in range(len(ab)):
                keyb.tap(k.backspace)
            keyb.type(abbreviations[ab])
            break



def on_release(Key):
    global key, key2
    key = ""
    key2 = Key


def is_pressed(Key):
    if key == KeyCode(char=Key):
        return True
    else:
        return False


def press1(Key):
    time.sleep(0.1)
    keyb.press(KeyCode(char=Key))


def release(Key):
    keyb.release(KeyCode(char=Key))


def wait(Key="]]"):
    while KeyCode(char=Key) != key:
        pass


def add_abbreviation(abbrev, replacement):
    global abbreviations
    abbreviations[abbrev] = replacement


def press_and_release(key1, key2):
    keyb.press(KeyCode(char=key1))
    keyb.release(KeyCode(char=key2))

def record(Key):
    global key_list

    zz = 0

    m = time.time()

    while key != KeyCode(char=Key):
        if key != "":
            zz += 1
            key_list[str(zz)] = [key, time.time() - m, "p"]
            m = time.time()
            b = key
            while key == b:
                pass
        elif key2 != "":
            zz += 1
            key_list[str(zz)] = [key2, time.time() - m, "r"]
            m = time.time()
            b = key2
            while key2 == b:
                pass
    key_list.pop("1")

    return key_list


def play(key_dict, speed_facor=1):
    for ke in key_dict.keys():
        time.sleep(key_dict[ke][1] / speed_facor)
        if key_dict[ke][2] == "p":
            keyb.press(key_dict[ke][0])
        else:
            keyb.release(key_dict[ke][0])


def add_hotkey(Key, do, args=""):
    global hotkeys
    hotkeys[Key] = [do, args]


l = Listener(on_press=on_press, on_release=on_release)

l.start()