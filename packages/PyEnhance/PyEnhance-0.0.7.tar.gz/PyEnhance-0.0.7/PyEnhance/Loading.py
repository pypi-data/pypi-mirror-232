import time
import threading as t
import shutil
from PyEnhance import Counter

Counter = Counter.Counter

Rotate = ['|', '/', '-', '\\', '|', '/', '-', '\\']


class Loading:

    def __init__(self):
        self.StopFlag = False
        self.thread = None

    def Stop(self):
        if self.thread.is_alive():
            self.StopFlag = True
            self.thread.join()

    def SpinStart(self, Text, TextBack):

        while self.StopFlag is False:
            for i in Rotate:
                if self.StopFlag: break
                print(f'{Text} {i}', end="", flush=True)
                time.sleep(0.4)
                print(f'{TextBack}', end="", flush=True)

    def Spin(self, Text):
        Text = Text
        textlen = len(Text)
        TextBack = '\b' * (textlen + 2)
        if self.thread is None or not self.SpinStart:
            self.thread = t.Thread(target=self.SpinStart, args=(Text, TextBack))
            self.thread.start()

    def BarStart(self, PrintSpeed):

        columns = shutil.get_terminal_size()

        Width = columns

        Width = Width.columns

        Range = Width

        while self.StopFlag is False:

            if self.StopFlag:
                break

            BufferBackSpace = '\b' * (Width)
            print(f"{BufferBackSpace}", end="")
            Text = 'Loading'
            Buffer = ' ' * 4
            SidesWidth = (Width - len(Text) + len(Buffer))

            for x in range(int(SidesWidth / 2)):

                if self.StopFlag: break

                print(f'|', end="", flush=True)
                time.sleep(PrintSpeed)

            for i in Buffer:

                if self.StopFlag: break

                print(f'{i}', end="", flush=True)
                time.sleep(PrintSpeed)

            for i in Text:

                if self.StopFlag: break

                print(f"{i}", end="", flush=True)
                time.sleep(PrintSpeed)

            for i in Buffer:
                if self.StopFlag: break

                print(f'{i}', end="", flush=True)
                time.sleep(PrintSpeed)

            for x in range(int(SidesWidth / 2)):

                if self.StopFlag: break

                print(f'|', end="", flush=True)
                time.sleep(PrintSpeed)

            Text = 'Loading'

            Buffer = ' ' * 4

            NewRange = Width + len(Buffer * 2)

            for i in range(int(NewRange)):

                if self.StopFlag: break

                print('\b', end="", flush=True)
                time.sleep(PrintSpeed)

    def Bar(self, PrintSpeed):

        if self.thread is None or not self.BarStart:
            self.thread = t.Thread(target=self.BarStart, args=(PrintSpeed,))
            self.thread.start()

    def StatsStart(self, List, ListCounter):
        CounterVal = ListCounter.Count

        ListLen = len(List)

        Progress = CounterVal / ListLen * 100

        Progress = str(Progress)

        if CounterVal == ListLen:
            OutputString = f"Progress: {CounterVal}/{ListLen}({Progress[:5]}%)"
            TextBack = '\b' * len(OutputString)
            print(f"{TextBack}{OutputString}", end="", flush=True)


        else:
            OutputString = f"Progress: {CounterVal}/{ListLen}({Progress[:4]}%)"
            TextBack = '\b' * len(OutputString)
            print(f"{TextBack}{OutputString}", end="", flush=True)

    def Stats(self, List, ListCounter):

        if self.thread is None or not self.thread.is_alive():
            self.thread = t.Thread(target=self.StatsStart, args=(List, ListCounter,))
            self.thread.start()


Loading = Loading()

"""

===EXAMPLES===

Stats:
    TestList = [1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,4,5,1,2,3,4,5]

    ListCounter = Counter

    for i in range(len(TestList)):

        time.sleep(1)

        ListCounter.Add()

        Loading.Stats(List=TestList, ListCounter=ListCounter)
"""
