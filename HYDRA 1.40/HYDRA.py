from socket import *
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.ttk import Treeview
from tkinter.ttk import Scrollbar
from tkinter.ttk import Progressbar
from threading import Thread
import traceback
import psutil
import time
import sys

class HYDRA:
    def __init__(self):
        self.connections = []
        self.start()
    def start(self):
        global filters
        filters = ["ALL"]
        for connection in psutil.net_connections():
            self.connections.append(connection)
            if not connection.status == "NONE": filters.append(connection.status)

class convert:
    def __init__(self, connection_obj):
        self.connection = connection_obj
    def string_obj(self):
        if self.connection.laddr == (): laddr = ""
        else:laddr = f"{self.connection.laddr.ip}"
        if self.connection.raddr == (): raddr = ""
        else:raddr = f"{self.connection.raddr.ip}"
        if self.connection.laddr == (): laddrp = ""
        else:laddrp = f"{self.connection.laddr.port}"
        if self.connection.raddr == (): raddrp = ""
        else:raddrp = f"{self.connection.raddr.port}"
        try:name = psutil.Process(self.connection.pid).name()
        except: name = "UNKNOWN"
        try:user = psutil.Process(self.connection.pid).username()
        except: user = "UNKNOWN"
        Data = {
            "name" : name,
            "pid" : self.connection.pid,
            "laddr" : laddr,
            "laddrp" : laddrp,
            "raddr" : raddr,
            "raddrp" : raddrp,
            "status" : self.connection.status,
            "user" : user
        }
        return Data

class GraphicUserInterface:
    def __init__(self):
        self.root = Tk()
        self.root.state("zoomed")
        self.root.title(f"HYDRA")

        self.TITLE = Label(
            self.root,
            text="HYDRA",
            fg="red",
            font=(
                "Helvetica",
                25
            ),
            anchor="w"
        )
        self.TITLE.pack(fill=BOTH)

        self.na_filter = "ALL"
        self.user_filter = "ALL"
        self.la_filter = "ALL"
        self.ra_filter = "ALL"
        self.lp_filter = "ALL"
        self.rp_filter = "ALL"
        self.st_filter = "ALL"

        filters = {"Process Name" : [self.na_filter, self.combo_evt_na, ""],
                  "Process User" : [self.user_filter, self.combo_evt_u, "readonly"],
                  "Local IP Address" : [self.la_filter, self.combo_evt_la, "readonly"],
                  "Remote IP Address" : [self.ra_filter, self.combo_evt_ra, "readonly"],
                  "Local Port" : [self.lp_filter, self.combo_evt_La, ""],
                  "Remote Port" : [self.rp_filter, self.combo_evt_Ra, ""],
                  "Process Status" : [self.st_filter, self.combo_evt_st, "readonly"]
        }
        self.filtersObj = {}

        self.FILTER_Frame = LabelFrame(
            self.root,
            text="FILTER"
        )
        self.FILTER_Frame.pack(fill=BOTH)

        for filter in filters:
            FilterFrame = Frame(self.FILTER_Frame)
            FilterFrame.pack(fill=BOTH)
            FilterLabel = Label(FilterFrame, text=f"{filter} \t: ")
            FilterLabel.pack(side="left", fill=BOTH)
            Filter = Combobox(
                FilterFrame,
                width=120,
                state=filters[filter][2]
            )
            Filter.bind("<<ComboboxSelected>>", filters[filter][1])
            Filter.bind("<Return>", filters[filter][1])
            Filter.pack(fill=BOTH)
            self.filtersObj[filter] = Filter

        self.LoaderFrame = LabelFrame(self.root)
        self.LoaderFrame.pack(fill=BOTH)

        self.Loader = Progressbar(self.LoaderFrame, length=300)
        self.Loader.pack(fill=BOTH)

        self.ConnectionsFrame = Frame(self.root)
        self.ConnectionsFrame.pack(fill=BOTH, expand=True)

        self.connections = Treeview(
            self.ConnectionsFrame,
            columns=(
                "PID",
                "User",
                "Local IP",
                "Local Port",
                "Remote IP",
                "Remote Port",
                "Status"
            ),
            height=20
        )
        self.WidthOfTree = 150
        self.connections.column(
            "#0",
            width=self.WidthOfTree,
            minwidth=self.WidthOfTree,
            stretch=YES
        )
        self.connections.heading(
            "#0",
            text="Name"
        )
        for column in self.connections["columns"]:
            self.connections.column(
                column,
                width=self.WidthOfTree,
                minwidth=self.WidthOfTree,
                stretch=YES
            )
            self.connections.heading(
                column,
                text=column
            )
        self.connections.bind("<Double-1>", self.info)
        self.connections.pack(fill=BOTH, expand=True, side="left")

        self.Scroll = Scrollbar(self.ConnectionsFrame, command=self.connections.yview)
        self.Scroll.pack(side="right", fill="y")

        self.connections.config(yscrollcommand=self.Scroll.set)

        self.name_filter()
        self.local_filter()
        self.remote_filter()
        self.rport_filter()
        self.lport_filter()
        self.status_filter()
        self.u_filter()
        self.update()

        for obj in self.filtersObj:
            self.filtersObj[obj].current(0)

        self.root.mainloop()
    def name_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["name"] == "UNKNOWN" and not result["name"] in filters: filters.append(result["name"])
        self.filtersObj["Process Name"]["values"] = filters
    def local_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["laddr"] == "NONE" and not result["laddr"] in filters: filters.append(result["laddr"])
        self.filtersObj["Local IP Address"]["values"] = filters
    def remote_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["raddr"] == "NONE" and not result["raddr"] in filters: filters.append(result["raddr"])
        self.filtersObj["Remote IP Address"]["values"] = filters
    def u_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["user"] == "NONE" and not result["user"] in filters: filters.append(result["user"])
        self.filtersObj["Process User"]["values"] = filters
    def lport_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["laddrp"] == "NONE" and not result["laddrp"] in filters: filters.append(result["laddrp"])
        self.filtersObj["Local Port"]["values"] = filters
    def rport_filter(self):
        filters = ["ALL"]
        for data in HYDRA().connections:
            data = convert(data)
            result = data.string_obj()
            if not result["raddrp"] == "NONE" and not result["raddrp"] in filters: filters.append(result["raddrp"])
        self.filtersObj["Remote Port"]["values"] = filters
    def status_filter(self):
        filters = ["ALL"]
        for conn in psutil.net_connections():
            if not conn.status == "NONE" and not conn.status in filters: filters.append(conn.status)
        self.filtersObj["Process Status"]["values"] = filters
    def update(self):
        t = Thread(target=self.update_support)
        t.daemon = True
        t.start()
    def update_support(self):
        self.connections.delete(*self.connections.get_children())
        Obj = HYDRA().connections
        self.Loader["maximum"] = len(Obj)
        self.Loader["value"] = 0
        for data in Obj:
            time.sleep(0.001)
            data = convert(data)
            result = data.string_obj()
            if result["name"] != self.na_filter and self.na_filter != "ALL": continue
            if result["laddr"] != self.la_filter and self.la_filter != "ALL": continue
            if result["raddr"] != self.ra_filter and self.ra_filter != "ALL": continue
            if result["status"] != self.st_filter and self.st_filter != "ALL": continue
            if result["user"] != self.user_filter and self.user_filter != "ALL": continue
            if result["laddrp"] != self.lp_filter and self.lp_filter != "ALL": continue
            if result["raddrp"] != self.rp_filter and self.rp_filter != "ALL": continue
            self.Loader["value"] += 1
            self.LoaderFrame.config(text=f"{self.Loader['value']}/{self.Loader['maximum']}")
            self.connections.insert(
                parent="",
                index=END,
                text=result["name"],
                values=(
                    result["pid"],
                    result["user"],
                    result["laddr"],
                    result["laddrp"],
                    result["raddr"],
                    result["raddrp"],
                    result["status"]
                )
            )
        self.Loader["value"] = self.Loader["maximum"]
        self.LoaderFrame.config(text=f"{self.Loader['value']}/{self.Loader['maximum']}")
        self.name_filter()
        self.local_filter()
        self.remote_filter()
        self.rport_filter()
        self.lport_filter()
        self.status_filter()
        self.u_filter()
        self.root.title(f"HYDRA - {time.strftime('%Y-%m/%d-%H:%M:%S')}")
    def combo_evt_na(self, event):
        self.na_filter = self.filtersObj["Process Name"].get()
        self.update()
    def combo_evt_la(self, event):  
        self.la_filter = self.filtersObj["Local IP Address"].get()
        self.update()
    def combo_evt_ra(self, event):
        self.ra_filter = self.filtersObj["Remote IP Address"].get()
        self.update()
    def combo_evt_La(self, event):
        self.lp_filter = self.filtersObj["Local Port"].get()
        self.update()
    def combo_evt_Ra(self, event):
        self.rp_filter = self.filtersObj["Remote Port"].get()
        self.update()
    def combo_evt_st(self, event):
        self.st_filter = self.filtersObj["Process Status"].get()
        self.update()
    def combo_evt_u(self, event):
        self.user_filter = self.filtersObj["Process User"].get()
        self.update()
    def info(self, evt):
        t = Thread(target=self.info_support)
        t.daemon = True
        t.start()
    def info_support(self):
        def open_files():
            OpenFilesFrame = Toplevel(InfoWin)
            OpenFilesFrame.title(f"Opend Files for {Info['name']}")
            Files = Listbox(OpenFilesFrame, width=120, height=30, font=("Arial", 8))
            Files.pack(fill=BOTH, expand=True)
            for info in Info["open_files"]:
                try:
                    Files.insert(END, str(info))
                except:
                    continue
        def connections():
            ConnectionsFrame = Toplevel(InfoWin)
            ConnectionsFrame.title(f"Connections for {Info['name']}")
            Connections = Listbox(ConnectionsFrame, width=120, height=30, font=("Arial", 8))
            Connections.pack(fill=BOTH, expand=True)
            for info in Info["connections"]:
                try:
                    Connections.insert(END, str(info))
                except:
                    continue
        def threads():
            ThreadsFrame = Toplevel(InfoWin)
            ThreadsFrame.title(f"Threads for {Info['name']}")
            Threads = Listbox(ThreadsFrame, width=120, height=30, font=("Arial", 8))
            Threads.pack(fill=BOTH, expand=True)
            for info in Info["threads"]:
                try:
                    Threads.insert(END, str(info))
                except:
                    continue
        def envrion():
            EnvironFrame = Toplevel(InfoWin)
            EnvironFrame.title(f"Envrionment for {Info['name']}")
            idx = 0
            MainFrame = Frame(EnvironFrame)
            MainFrame.pack(fill=BOTH, expand=True, side="left")
            for info in Info["environ"]:
                if idx > 30:
                    MainFrame = Frame(EnvironFrame)
                    MainFrame.pack(fill=BOTH, expand=True, side="left")
                    idx = 0
                idx += 1
                try:
                    EnvInfoFrame = Frame(MainFrame)
                    EnvInfoFrame.pack(fill=BOTH)
                    EnvInfoLabel = Label(EnvInfoFrame, text=str(info))
                    EnvInfoLabel.pack(fill=BOTH, side="left")
                    EnvInfo = Entry(EnvInfoFrame, width=50)
                    EnvInfo.pack(fill=BOTH, side="right")
                    EnvInfo.insert(END, str(Info["environ"][info]))
                except:
                    EnvInfoFrame.destroy()
                    continue
        def terminate():
            try:
                ask = messagebox.askyesno("Do you wish to continue?", "Do you wish to terminate this process?")
                if ask == True:
                    Obj.terminate()
                    InfoWin.destroy()
                    self.update()
            except:
                messagebox.showerror("Error", traceback.format_exc())
        def kill():
            try:
                ask = messagebox.askyesno("Do you wish to continue?", "Do you wish to kill this process?")
                if ask == True:
                    Obj.kill()
                    InfoWin.destroy()
                    self.update()
            except:
                messagebox.showerror("Error", traceback.format_exc())
        Item = self.connections.item(self.connections.selection()[0])
        PID = Item["values"][0]
        Obj = psutil.Process(PID)
        Info = Obj.as_dict()
        InfoWin = Toplevel(self.root)
        InfoWin.resizable(False, False)
        InfoWin.title(f"Management for {Info['name']}")
        HeadFrame = Frame(InfoWin)
        HeadFrame.pack(fill=BOTH)
        TITLE = Label(HeadFrame, text=Info["name"], font=("Arial", 15))
        TITLE.pack(side="left")
        ButtonWidth = 10
        TButton = Button(HeadFrame, text="Terminate", command=terminate, width=ButtonWidth, foreground="red")
        TButton.pack(side="right")
        KButton = Button(HeadFrame, text="Kill", command=kill, width=ButtonWidth, foreground="red")
        KButton.pack(side="right")
        FButton = Button(HeadFrame, text="Files", command=open_files, width=ButtonWidth)
        FButton.pack(side="right")
        CButton = Button(HeadFrame, text="Connections", command=connections, width=ButtonWidth)
        CButton.pack(side="right")
        ThButton = Button(HeadFrame, text="Threads", command=threads, width=ButtonWidth)
        ThButton.pack(side="right")
        EButton = Button(HeadFrame, text="Environ", command=envrion, width=ButtonWidth)
        EButton.pack(side="right")
        LoaderFrame = LabelFrame(InfoWin)
        LoaderFrame.pack(fill=BOTH, expand=True)
        Loader = Progressbar(LoaderFrame, length=300)
        Loader.pack(fill=BOTH)
        Loader["maximum"] = len(Info)
        for option in Info:
            Loader["value"] += 1
            LoaderFrame.config(text=f"{int(Loader['value'])}/{len(Info)}")
            try:
                if str(option).lower() in ["open_files", "connections", "threads", "environ", "memory_maps"]:
                    continue
                InfoFrame = Frame(InfoWin)
                InfoFrame.pack(fill=BOTH)
                InfoLabel = Label(InfoFrame, text=f"{str(option).upper()}", anchor="w")
                InfoLabel.pack(side="left")
                InfoResult = Entry(InfoFrame, width=120)
                InfoResult.insert(END, Info[option])
                InfoResult.pack(fill=BOTH, side="right")
            except:
                InfoFrame.destroy()
                continue
            
gui = GraphicUserInterface()
