from socket import *
from threading import Thread
import traceback
import requests
import psutil
import os
import sys

Local_Version = "2.0.0"

settings = {}

class DefaultSetting:
    def __init__(self):
        self.Settings = {
            "Shell.net.track.url" : "http://ip-api.com/json/[ip]",
            "Shell.net.stat.local" : "[[laddr]]:[laddrp]",
            "Shell.net.stat.remote" : "[[raddr]]:[raddrp]",
            "Shell.net.stat.unknown" : "?",
            "Shell.process.list.value" : "_name;_pid;",
            "Shell.process.fullinfo.limit" : "10",
        }
        self.run()
    def run(self):
        for setting in self.Settings:
            settings[setting] = self.Settings[setting]

class Core:
    def __init__(self, PID:int):
        self.PID = PID
        self.Process = psutil.Process(PID)
        self.Data = self.Process.as_dict()
    def kill(self):
        self.Process.kill()
    def terminate(self):
        self.Process.terminate()
    def update(self):
        self.Process = psutil.Process(self.PID)
        self.Data = self.Process.as_dict()
    def data(self):
        return self.Data

class Shell:
    class process:
        def list(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Show all process (process.list)'''
            try:
                idx = 0
                processList = {str(proc.name()): proc for proc in psutil.process_iter()}
                processList = {key: processList[key] for key in sorted(processList)}
                tabSize = max(len(key) for key in processList.keys()) + 5
                for idx, proc in enumerate(processList, start=0):
                    try:
                        idx += 1
                        Text = ""
                        titleValue = str(settings["Shell.process.list.value"]).split(";")[0]
                        try:
                            if titleValue == "": continue
                            data = str(getattr(processList[proc], titleValue)())
                            Text += f"\033[0;36m{data}\033[0m{' ' * (tabSize - len(str(data)))}"
                        except:
                            try:
                                data = str(processList[proc].__dict__[titleValue])
                                Text += f"\033[0;36m{data}\033[0m{' ' * (tabSize - len(str(data)))}"
                            except:
                                Text += f"{' ' * tabSize}"
                        for value in str(settings["Shell.process.list.value"]).split(";")[1:]:
                            try:
                                if value == "": continue
                                data = str(getattr(processList[proc], value)())
                                Text += f"\033[0;32m{data}\033[0m{' ' * (tabSize - len(str(data)))}"
                            except:
                                try:
                                    data = str(processList[proc].__dict__[value])
                                    Text += f"\033[0;32m{data}\033[0m{' ' * (tabSize - len(str(data)))}"
                                except:
                                    Text += f"{' ' * tabSize}"
                                    continue
                        print(f"{idx}.{' ' * (6 - len(str(idx)))}{Text}")
                    except:
                        continue
            except:
                raise 
        def fullinfo(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Show all data from process (process.fullinfo [PID])'''
            try:
                PID = int(args[0])
                obj = Core(PID)
                obj.update()
                ProcessData = obj.data()
                ProcessData = {key: ProcessData[key] for key in sorted(ProcessData)}
                tabSize = max(len(key) for key in ProcessData.keys()) + 5
                for data in ProcessData:
                    DataType = str(type(ProcessData[data])).split("'")[1]
                    if DataType == "list":
                        idx2 = 0
                        print(f"\033[0;36m{data}:\033[0m")
                        for subdata in ProcessData[data]:
                            idx2 += 1
                            print("\t", f"\033[0;32m{subdata}\033[0m")
                            if idx2 > int(settings["Shell.process.fullinfo.limit"]):
                                print("\t\033[0;31m(Use process.info for more detail)\033[0m")
                                break
                        print()
                    elif DataType == "dict":
                        print(f"\033[0;36m{data}:\033[0m")
                        if len(ProcessData[data]) == 0:
                            continue
                        DataList = ProcessData[data]
                        DataList = {key: DataList[key] for key in sorted(DataList)}
                        subtabSize = max(len(key) for key in DataList.keys()) + 5
                        idx2 = 0
                        for subdata in DataList:
                            idx2 += 1
                            print("\t", f"\033[0;36m{subdata}\033[0m{' ' * (subtabSize - len(subdata))}: \033[0;32m{ProcessData[data][subdata]}\033[0m")
                            if idx2 > int(settings["Shell.process.fullinfo.limit"]):
                                print("\t\033[0;31m(Use process.info for more detail)\033[0m")
                                break
                        print()
                    else:
                        print(f"\033[0;36m{data}\033[0m{' ' * (tabSize - len(data))}: \033[0;32m{ProcessData[data]}\033[0m")
            except:
                raise 
        def info(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Show one data from process (process.fullinfo [PID] [DataKey])'''
            try:
                PID = int(args[0])
                target = str(args[1])
                obj = Core(PID)
                obj.update()
                ProcessData = obj.data()
                ProcessData = {key: ProcessData[key] for key in sorted(ProcessData)}
                tabSize = max(len(key) for key in ProcessData.keys()) + 5
                for data in ProcessData:
                    if not data == target: continue
                    DataType = str(type(ProcessData[data])).split("'")[1]
                    if DataType == "list":
                        print(f"\033[0;36m{data}:\033[0m")
                        idx2 = 0
                        for subdata in ProcessData[data]:
                            idx2 += 1
                            print(f"\t{idx2}.")
                            subDataType = str(type(subdata)).split("'")[1]
                            if subDataType.startswith("psutil"):
                                subdataList = subdata.__dir__()
                                subtabSize = max(len(key) for key in subdataList) + 3
                                for objdata in subdataList:
                                    if objdata.startswith("_"): continue
                                    value = getattr(subdata, objdata)
                                    if str(value).startswith("<"): continue
                                    print(f"\t\t\033[0;36m{objdata}\033[0m{' ' * (subtabSize - len(objdata))}= \033[0;32m{str(value)}\033[0m")
                            else:
                                print("\t", f"\033[0;32m{subdata}\033[0m")
                        print()
                    elif DataType == "dict":
                        print(f"\033[0;36m{data}:\033[0m")
                        if len(ProcessData[data]) == 0:
                            continue
                        DataList = ProcessData[data]
                        DataList = {key: DataList[key] for key in sorted(DataList)}
                        subtabSize = max(len(key) for key in DataList.keys()) + 5
                        for subdata in DataList:
                            print("\t", f"\033[0;36m{subdata}\033[0m{' ' * (subtabSize - len(subdata))}: \033[0;32m{ProcessData[data][subdata]}\033[0m")
                        print()
                    elif DataType.startswith("psutil"):
                        print(f"\033[0;36m{data}:\033[0m")
                        subdataList = ProcessData[data].__dir__()
                        subtabSize = max(len(key) for key in subdataList) + 3
                        for objdata in subdataList:
                            if objdata.startswith("_"): continue
                            value = getattr(ProcessData[data], objdata)
                            if str(value).startswith("<"): continue
                            print(f"\t\033[0;36m{objdata}\033[0m{' ' * (subtabSize - len(objdata))}= \033[0;32m{str(value)}\033[0m")
                        print()
                    else:
                        print(f"\033[0;36m{data}\033[0m{' ' * (tabSize - len(data))}: \033[0;32m{ProcessData[data]}\033[0m")
            except:
                raise 
        def terminate(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Terminate process (process.terminate [PID])'''
            try:
                PID = int(args[0])
                obj = Core(PID)
                obj.update()
                obj.terminate()
                print(f"\033[0;36m[+] Process has been successfully terminated:\033[0m \033[0;32m{obj.data()['name']}\033[0m")
            except:
                raise
        def kill(*args):
            if args[0] == "help":
                return '''Kill process (process.terminate [PID])'''
            try:
                PID = int(args[0])
                obj = Core(PID)
                obj.update()
                obj.kill()
                print(f"\033[0;36m[+] Process has been successfully killed:\033[0m \033[0;32m{obj.data()['name']}\033[0m")
            except:
                raise
    class net:
        def stat(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Show all network connection from process (net.stat)'''
            try:
                idx = 0
                processList = {}
                for proc in psutil.net_connections():
                    try:
                        ProcessName = str(psutil.Process(proc.pid).name())
                        ProcessObj = psutil.Process(proc.pid)
                        if proc.laddr == (): laddr = settings["Shell.net.stat.unknown"]
                        else:laddr = f"{proc.laddr.ip}"
                        if proc.raddr == (): raddr = settings["Shell.net.stat.unknown"]
                        else:raddr = f"{proc.raddr.ip}"
                        if proc.laddr == (): laddrp = settings["Shell.net.stat.unknown"]
                        else:laddrp = f"{proc.laddr.port}"
                        if proc.raddr == (): raddrp = settings["Shell.net.stat.unknown"]
                        else:raddrp = f"{proc.raddr.port}"
                        Local = str(settings["Shell.net.stat.local"]).replace("[laddr]", laddr).replace("[laddrp]", laddrp)
                        Remote = str(settings["Shell.net.stat.remote"]).replace("[raddr]", raddr).replace("[raddrp]", raddrp)
                        idx2 = 0
                        while True:
                            idx2 += 1
                            FormatName = ProcessName + "::::" + str(idx2)
                            if not FormatName in processList:
                                processList[FormatName] = {
                                    "obj" : ProcessObj,
                                    "conn" : {
                                        "local" : Local,
                                        "remote" : Remote
                                    }
                                }
                                break
                    except:
                        try:
                            ProcessName = settings["Shell.net.stat.unknown"]
                            ProcessObj = None
                            if proc.laddr == (): laddr = settings["Shell.net.stat.unknown"]
                            else:laddr = f"{proc.laddr.ip}"
                            if proc.raddr == (): raddr = settings["Shell.net.stat.unknown"]
                            else:raddr = f"{proc.raddr.ip}"
                            if proc.laddr == (): laddrp = settings["Shell.net.stat.unknown"]
                            else:laddrp = f"{proc.laddr.port}"
                            if proc.raddr == (): raddrp = settings["Shell.net.stat.unknown"]
                            else:raddrp = f"{proc.raddr.port}"
                            Local = str(settings["Shell.net.stat.local"]).replace("[laddr]", laddr).replace("[laddrp]", laddrp)
                            Remote = str(settings["Shell.net.stat.remote"]).replace("[raddr]", raddr).replace("[raddrp]", raddrp)
                            idx2 = 0
                            while True:
                                idx2 += 1
                                FormatName = ProcessName + "::::" + str(idx2)
                                if not FormatName in processList:
                                    processList[FormatName] = {
                                        "obj" : ProcessObj,
                                        "conn" : {
                                            "local" : Local,
                                            "remote" : Remote
                                        }
                                    }
                                    break
                        except:
                            continue
                processList = {key: processList[key] for key in sorted(processList)}
                tabSize = max(len(key) for key in processList.keys()) + 5
                print(f"Index{' ' * (6 - len(str('Index')))} ProcessName{' ' * (tabSize - len(str('ProcessName')))}ProcessID{' ' * (tabSize - len(str('ProcessID')))}Local{' ' * (40 - len(str('Local')))}     Remote")
                for proc in processList:
                    try:
                        idx += 1
                        ProcessName = str(proc).split("::::")[0]
                        try:
                            ProcessID = processList[proc]["obj"].pid
                        except:
                            ProcessID = "?"
                        Local = processList[proc]["conn"]["local"]
                        Remote = processList[proc]["conn"]["remote"]
                        print(f"{idx}.{' ' * (6 - len(str(idx)))}\033[0;36m{ProcessName}\033[0m{' ' * (tabSize - len(str(ProcessName)))}\033[0;32m{ProcessID}\033[0m{' ' * (tabSize - len(str(ProcessID)))}\033[0;32m{Local}{' ' * (40 - len(str(Local)))}-->  {Remote}\033[0m")
                    except:
                        continue
            except:
                raise 
        def track(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Show ISP external ip address track result. Type 'all' to see all track results from your process. (net.track [IP])'''
            try:
                ip = str(args[0])
                if ip == "all":
                    already = []
                    for proc in psutil.net_connections():
                        ip = proc.raddr
                        if ip == (): continue
                        ip = ip[0]
                        if ip in already: continue
                        print(f"-" * 50 + "[" + psutil.Process(proc.pid).name() + "]" + "-" * 50)
                        url = str(settings["Shell.net.track.url"]).replace("[ip]", ip)
                        r = requests.get(url)
                        json = r.json()
                        result = {data: json[data] for data in json}
                        tabSize = max(len(key) for key in result.keys()) + 5
                        for data in result:
                            print(f"\033[0;36m{data.upper()}\033[0m{' ' * (tabSize - len(str(data.upper())))}: \033[0;32m{result[data]}\033[0m")
                        already.append(ip)
                else:
                    url = str(settings["Shell.net.track.url"]).replace("[ip]", ip)
                    r = requests.get(url)
                    json = r.json()
                    result = {data: json[data] for data in json}
                    tabSize = max(len(key) for key in result.keys()) + 5
                    for data in result:
                        print(f"\033[0;36m{data.upper()}\033[0m{' ' * (tabSize - len(str(data.upper())))}: \033[0;32m{result[data]}\033[0m")
            except:
                raise
    class var:
        def set(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Set local variable'''
            try:
                target = str(args[0])
                value = str(args[1])
                if target in settings:
                    old = settings[target]
                    settings[target] = value
                    print(f"\033[0;36m[+] Variable successfully changed:\033[0m \033[0;32m{old}\033[0m --> \033[0;32m{value}\033[0m")
                elif not target in settings:
                    print(f"\033[0;31m[-] Variable change failed: variable not exists\033[0m")
                else:
                    print(f"\033[0;31m[-] Variable change failed: Unknown\033[0m")
            except:
                raise
        def print(*args):
            if len(args) > 0 and args[0] == "help":
                return '''print local variable. Type 'all' to see all local variables'''
            try:
                target = str(args[0])
                if target in settings:
                    print(f"\033[0;36m{target}\033[0m{' ' * (32 - len(str(target)))}: \033[0;32m{settings[target]}\033[0m")
                elif target == "all":
                    for key in settings:
                        print(f"\033[0;36m{key}\033[0m{' ' * (32 - len(str(key)))}: \033[0;32m{settings[key]}\033[0m")
                elif not target in settings:
                    print(f"\033[0;31m[-] Variable print failed: variable not exists\033[0m")
                else:
                    print(f"\033[0;31m[-] Variable print failed: Unknown\033[0m")
            except:
                raise
        def reset(*args):
            if len(args) > 0 and args[0] == "help":
                return '''Reset local variables'''
            DefaultSetting()

class Handler:
    def __init__(self, command):
        self.COMMAND = str(command)
        self.ObjectSplit = "."
        self.ArgumentsSplit = " "
        self.arguments = []
        self.object = Shell
    def execute(self):
        Type = self.COMMAND.split(self.ObjectSplit)[0]
        Func = self.COMMAND.split(self.ObjectSplit)[1].split(self.ArgumentsSplit)[0]
        arguments = self.COMMAND.split(self.ArgumentsSplit)[1:]
        getattr(getattr(self.object, Type), Func)(*arguments)

if __name__ == "__main__":
    DefaultSetting()
    while True:
        try:
            command = str(input(f"<HYDRA {Local_Version}>"))
            if command == "clear" or command == "cls":
                os.system("cls" if os.name == "nt" else "clear")
            elif command == "exit":
                break
            elif command == "help":
                for Type in Shell.__dict__:
                    if not Type.startswith("__"):
                        print(f"[{Type}]")
                        commands = getattr(Shell, Type).__dict__
                        tabSize = max(len(key) for key in commands.keys()) + 15
                        for func in commands:
                            if not func.startswith("__"):
                                print(f"{Type}.{func}{' ' * (tabSize - len(f'{Type}.{func}'))}{getattr(getattr(Shell, Type), func)('help')}")
                        print()
            else:
                obj = Handler(command=command)
                obj.execute()
        except:
            print(f"\033[0;31m{traceback.format_exc()}\033[0m")
