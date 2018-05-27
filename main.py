import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json

root = Tk();
root.title("node-godwatch server")
root.geometry("300x300");
root.resizable(0, 0);

str_server = StringVar();
str_username = StringVar();
str_password = StringVar();

lsvar_current_address = StringVar();
lsvar_current_client = StringVar();

# METHODS
def retrieve_data():

    r = requests.get('http://' + str_server.get() + '/config', auth=(str_username.get(), str_password.get()));

    if r.status_code == 200:

        data = json.loads(r.text)[0];

        # PARSE CLIENTS
        lsvar_current_client.set('');
        ls_clients['menu'].delete(0, 'end');

        for x in data['clients']:
            rc = requests.get('http://' + str_server.get() + '/clients/' + str(x), auth=(str_username.get(), str_password.get()));

            if rc.status_code == 200:
                rcd = json.loads(rr.text);
                ls_clients['menu'].add_command(label=rcd['name'], command=tk._setit(lsvar_current_client, rcd['name']));

        # PARSE RECIPIENTS
        lsvar_current_address.set('');
        ls_addresses['menu'].delete(0, 'end');

        for x in data['recipients']:
            rr = requests.get('http://' + str_server.get() + '/recipients/' + str(x), auth=(str_username.get(), str_password.get()));

            if rr.status_code == 200:
                rrd = json.loads(rr.text);
                ls_addresses['menu'].add_command(label=rrd['name'], command=tk._setit(lsvar_current_address, rrd['name']));

def load_settings():
    settings_file = open('settings.txt', 'w+');
    
    try:
        settings = settings_file.readlines();
        str_server.set(settings[0][:-1]);
        str_username.set(settings[1][:-1]);
        str_password.set(settings[2][:-1]);
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n');
    settings_file.close();

# GUI
mw = ttk.Notebook(root, width=300, height=300);

# CONFIG PAGE
config_page = Frame(mw, padx=10, pady=10);

config_page_f1 = Frame(config_page);
label_server = Label(config_page_f1, text="Server");
input_server = Entry(config_page_f1, textvariable=str_server);
input_server.insert(0, "server:port");
label_server.grid(row=1,column=1);
input_server.grid(row=1,column=2);

label_username = Label(config_page_f1, text="Username");
input_username = Entry(config_page_f1, textvariable=str_username);
label_username.grid(row=2,column=1);
input_username.grid(row=2,column=2);

label_password = Label(config_page_f1, text="Password");
input_password = Entry(config_page_f1, textvariable=str_password, show="*");
label_password.grid(row=3,column=1);
input_password.grid(row=3,column=2);
config_page_f1.grid(row=1,column=1);

config_page_f2 = Frame(config_page);
button_saveSettings = Button(config_page_f2, text="Save", command=save_settings);
button_saveSettings.grid(row=1,column=1);
button_retrieveData = Button(config_page_f2, text="Retrieve", command=retrieve_data);
button_retrieveData.grid(row=1,column=2);
config_page_f2.grid(row=2,column=1)

# CLIENT PAGE
client_page = Frame(mw, padx=10, pady=10);

client_page_f1 = Frame(client_page);
ls_clients = OptionMenu(client_page_f1, lsvar_current_client, {"None"});
ls_clients.grid(row=1,column=1);
client_page_f1.grid(row=1,column=1);

# RECIPIENT PAGE
address_page = Frame(mw, padx=10, pady=10);

address_page_f1 = Frame(address_page);
ls_addresses = OptionMenu(address_page_f1, lsvar_current_address, {"None"});
ls_addresses.grid(row=1,column=1);
address_page_f1.grid(row=1,column=1);

mw.add(config_page, text="Config");
mw.add(client_page, text="Clients");
mw.add(address_page, text="Recipients");

mw.grid(row=1,column=1);

load_settings();

root.mainloop();
