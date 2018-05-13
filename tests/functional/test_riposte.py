ARROW_UP = "\033[A"
ARROW_DOWN = "\033[B"


def test_commands_and_history(sut):
    sut.sendline("bar")
    sut.expect("bar executed\r\nsut >")

    sut.sendline("foo scoo bee")
    sut.expect("foo executed with scoo bee\r\nsut > ")

    sut.send(ARROW_UP)
    sut.expect("foo scoo bee")
    sut.send(ARROW_UP)
    sut.expect("\rsut > bar         \x08\x08\x08\x08\x08\x08\x08\x08\x08")
    sut.send(ARROW_DOWN)
    sut.expect("\x08\x08\x08foo scoo bee")
    sut.send(ARROW_DOWN)
    sut.expect("\rsut >             \rsut > ")


def test_command_specific_completer(sut):
    sut.send("foo \t\t")
    sut.expect("\r\naaa  abba bbb  ddd \r\n\r\r\nsut > foo ")
    sut.send("a\t\t")
    sut.expect("\r\naaa  abba\r\n\r\r\nsut > foo a")
    sut.send("b\t")
    sut.expect("ba")
