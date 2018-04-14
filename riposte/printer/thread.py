import queue
import threading
import typing

printer_queue = queue.Queue()


class PrintResource(typing.NamedTuple):
    content: tuple
    sep: str
    end: str
    file: typing.IO


class PrinterThread(threading.Thread):
    def __init__(self):
        super(PrinterThread, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            resource = PrintResource(*printer_queue.get())
            print(
                *resource.content,
                sep=resource.sep,
                end=resource.end,
                file=resource.file,
            )
            printer_queue.task_done()

    @staticmethod
    def wait():
        printer_queue.join()

    def put(self, resource: PrintResource):
        printer_queue.put(resource)
