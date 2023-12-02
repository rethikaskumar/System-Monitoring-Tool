# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:36:32 2023

@author: DELL
"""

from tkinter import *
from tkinter import ttk
import time
import psutil
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import datetime
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tkinter import messagebox
import wmi
from PIL import ImageTk, Image

LARGEFONT =("Verdana", 25)

#============GOOGLE DRIVE AUTHORIZATION=================================================
gauth = GoogleAuth()       
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth) 

#=============CPU USAGE GRAPH===========================================================
def plot_cpu():
    #x=[datetime.datetime.now()+datetime.timedelta(seconds=i) for i in range(10)]
    x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    cpu=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    w2=Toplevel(window)
    w2.geometry('500x500')
    w2.title("CPU Usage")
    w2.configure(bg='white')
    w2.maxsize(500, 500)
    label=Label(w2, text="CPU Usage", font=LARGEFONT, bg='White')
    label.place(relx=0.35, rely=0.1)
    
    #figure, ax = plt.subplots(figsize=(10, 8))
    
    plt.ion()
    figure=plt.figure()
    ax=figure.add_subplot(111)
    #ax.set(xlabel=None)
    ax.set_xticklabels([])
    
    line1, = ax.plot(x, cpu, 'b-')
    ax.set_xlim([0, 9])
    ax.set_ylim([0, 110])
    canvas = FigureCanvasTkAgg(figure, master = w2)  
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.1, rely=0.2)
    while(1):
        cpu.append(psutil.cpu_percent(1))
        cpu=cpu[1:]
        #ax.set_xlim([datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(seconds=9)])
        line1.set_xdata(x)
        line1.set_ydata(cpu)
        canvas.draw()
        canvas.flush_events()
        time.sleep(0.1)

#=================RAM USAGE CHART======================================================
def plot_ram():
    #x=[datetime.datetime.now()+datetime.timedelta(seconds=i) for i in range(10)]
    ut=psutil.virtual_memory()[2]
    x=['Used ('+str(ut)+')', 'Unused ('+str(100-ut)+')']
    ram=[ut, 100-ut]
    
    w2=Toplevel(window)
    w2.geometry('500x500')
    w2.title("CPU Usage")
    w2.configure(bg='white')
    
    #figure, ax = plt.subplots(figsize=(10, 8))
    
    plt.ion()
    figure=plt.figure()
    
    plt.pie(ram, labels=x)
    canvas = FigureCanvasTkAgg(figure, master = w2)  
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.1, rely=0.2)

#=================DISPLAY RUNNING PROCESSES SORTED BY RAM USAGE=========================
def get_processlist():
    w2=Toplevel(window)
    w2.geometry('500x500')
    w2.title("Process List")
    w2.configure(bg='white')
    list_processes=[]
    for proc in psutil.process_iter():
        try:
            pinfo=proc.as_dict(attrs=['pid', 'name', 'username', 'memory_percent'])
            pinfo['vms']=proc.memory_info().vms
            list_processes.append(pinfo)
        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    list_processes=sorted(list_processes, key=lambda procObj: procObj['memory_percent'], reverse=True)
    #print(list_processes)
    i=3
    #for elem in list_processes:
        #Label (w2, text = elem['name']+' '+str(elem['memory_percent'])).grid(row=i)
        #i=i+1
    scroll_bar = Scrollbar(w2)
    scroll_bar.pack( side = RIGHT,fill = Y )
    mylist = Listbox(w2, yscrollcommand = scroll_bar.set )
    mylist.insert(END, 'Number of active processes: '+str(len(list_processes)))
    for i in list_processes:
        mylist.insert(END, i['name'] + "     ("+ str(i['memory_percent'])[:4] + ")")
    
    mylist.pack( side = LEFT, fill = BOTH , expand=True)
    scroll_bar.config( command = mylist.yview )


#====================TERMINATE CHOSEN PROCESS SAFELY====================================
def terminateProcess():
    w2=Toplevel(window)
    w2.geometry('500x500')
    w2.title("Terminate process")
    w2.configure(bg='white')
    def checkcmbo():
        name=processchosen.get()
        print(name)
        ti=0
        f = wmi.WMI()
      
        for process in f.Win32_Process():
         
            if process.name == name:
                try:
                    process.Terminate()
         
                    ti += 1
                except:
                    pass
    
        if ti == 0:
            messagebox.showerror("error", "Process not found!!!")
    n = StringVar()
    processchosen = ttk.Combobox(w2, width = 27, textvariable = n)
    list_processes=[]
    for proc in psutil.process_iter():
        try:
            pinfo=proc.as_dict(attrs=['name'])
            list_processes.append(pinfo)
        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    processchosen['values']=[str(i.values())[14:-3] for i in list_processes]
    processchosen.place(relx=0.3, rely=0.5)
    labelc=Label(w2, text="Choose process to terminate", font="Garamond", bg='White').place(relx=0.25, rely=0.4)
    btn = ttk.Button(w2, text="Terminate",command=checkcmbo)
    btn.place(relx=0.4, rely=0.6)

#==================SYNC UNUSED FILES TO GOOGLE DRIVE======================================
def modifiedfiles():
    file_list = drive.ListFile({'q': "'1mkVIN_1bxOIuQw_WLliOiM6OPKaiSNL3' in parents and trashed=false"}).GetList()
    #print(file_list)
    lastmodtime=datetime.datetime.now()
    #comp=datetime.datetime(1111, 1, 1, 1, 0, 0)
    files1=[]
    for(root, dirs, file) in os.walk('D:\\ospackage'):
        for f in file:
            #print(type(f))
            files1.append(root+'\\'+f)

    files1.sort(key=lambda x: os.path.getmtime(x))
    for f in files1:
        #print(f)
        flag=0
        modified_time = os.path.getmtime(f)
        convert_time = time.localtime(modified_time)
        format_time = time.strftime('%d%m%Y %H:%M:%S', convert_time)
        datetime_object = datetime.datetime.strptime(format_time, '%d%m%Y %H:%M:%S')
        lastmod=(datetime.datetime.now()-datetime_object)
        #print(datetime.timedelta(hours=1))
        if lastmod > datetime.timedelta(hours=1):
            if len(file_list)>=1:
                for drivefile in file_list:
                    if drivefile['title']==f:
                        flag=1
            if flag==0:
                print(f)
                upload_file=f
                file = drive.CreateFile({
                    'title': "{}".format(upload_file),
                    "parents": [{"id": '1mkVIN_1bxOIuQw_WLliOiM6OPKaiSNL3'}]
                    })
                file.SetContentFile(upload_file)
                file.Upload()
                file.clear()
        else:
            break
    file_list = drive.ListFile({'q': "'1mkVIN_1bxOIuQw_WLliOiM6OPKaiSNL3' in parents and trashed=false"}).GetList()
    for f in files1:
        for drivefile in file_list:
            if drivefile['title']==f:
                try:
                    os.remove(f)
                except:
                    messagebox.showerror("Error", f+" is used by another process")
    messagebox.showinfo("Sync Files", "All recently unmodified files have been uploaded successfully\n Last uploaded "+str(lastmodtime))
        
    
        
window=Tk()
width=window.winfo_screenwidth()
height=window.winfo_screenheight()
window.title('System monitoring tool')
window.geometry('1000x1000')


#window.geometry('%dx%d'%(width,height))
#window.resizable(False, False)
#image=Image.open('ScxKID.png')
#img2=image.resize((width,height))
#img3=ImageTk.PhotoImage(img2)
#l=Label(window, image=img3)
#l.pack(side='top', fill=Y, expand=True)


l1=Label(window, text=" System Monitoring Tool ", font=('Garamond',30), bg='White').place(relx=0.3, rely=0.1)
cpu_button=Button(master=window, height=4, width=20, text='CPU Usage',font=('Garamond',15), command=plot_cpu)
cpu_button.place(relx=0.25, rely=0.2)
ram_button=Button(master=window, height=4, width=20, text='RAM usage',font=('Garamond',15), command=plot_ram)
ram_button.place(relx=0.5, rely=0.2)
processlist_button=Button(master=window, height=4, width=20, text='Process List',font=('Garamond',15), command=get_processlist)
processlist_button.place(relx=0.25, rely=0.4)
sync_button=Button(master=window, height=4, width=20, text='Sync Files', font=('Garamond',15),command=modifiedfiles)
sync_button.place(relx=0.38, rely=0.6)
terminate_button=Button(master=window, height=4, width=20, text='Terminate Process',font=('Garamond',15), command=terminateProcess)
terminate_button.place(relx=0.5, rely=0.4)

window.configure(bg='White')
window.mainloop()


