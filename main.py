import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json

root = Tk();
root.title("node-Godwatch Administrator")
root.geometry("300x300");
root.resizable(0, 0);

str_server = StringVar();
str_server.set("");
str_username = StringVar();
str_password = StringVar();

str_rname = StringVar();
str_rname.set("");
str_raddress = StringVar();
str_raddress.set("");

lsvar_current_address = StringVar();
lsvar_current_client = StringVar();

db_addresses = {};
db_clients = {};

# METHODS
def retrieve_data():

    if str_server.get() != "":

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
                    if not rcd is None:
                        ls_clients['menu'].add_command(label=rcd['name'], command=tk._setit(lsvar_current_client, rcd['name']));
                        db_clients[rcd['name']] = rcd;

            # PARSE RECIPIENTS
            lsvar_current_address.set('');
            ls_addresses['menu'].delete(0, 'end');

            for x in data['recipients']:
                rr = requests.get('http://' + str_server.get() + '/recipients/' + str(x), auth=(str_username.get(), str_password.get()));

                if rr.status_code == 200:
                    rrd = json.loads(rr.text);
                    if not rrd is None:
                        ls_addresses['menu'].add_command(label=rrd['name'], command=tk._setit(lsvar_current_address, rrd['name']));
                        db_addresses[rrd['name']] = rrd;

def load_settings():
    try:
        settings_file = open('settings.txt', 'r+');
    except IOError:
        settings_file = open('settings.txt', 'w+');

    try:
        settings = settings_file.readlines();
        str_server.set(settings[0][:-1]);
        str_username.set(settings[1][:-1]);
        str_password.set(settings[2][:-1]);
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def dropdown_change_recipient(*args):
    name = lsvar_current_address.get();
    if name != "" and name != "{'None'}":
        data = db_addresses[name];
        str_rname.set(data['name']);
        str_raddress.set(data['address']);

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n');
    settings_file.close();

def check_empty_address():
    if str_rname.get() != "":
        if str_raddress.get() != "":
            return True;
        else:
            return False:
    else:
        return False:

def save_address():
    if check_empty_address():
        name = lsvar_current_address.get();
        if name != "" and name != "{'None'}":
            odata = db_addresses[name];
            data = {}
            data['name'] = str_rname.get();
            data['address'] = str_raddress.get();
            data['enabled'] = True;
            r = requests.put('http://' + str_server.get() + '/recipients/' + str(odata['rid']), auth=(str_username.get(), str_password.get()), json={ 'name': data['name'], 'address': data['address'], 'enabled': data['enabled'] });
            retrieve_data();
        else:
            save_address_as_new();

def save_address_as_new():
    if check_empty_address():
        data = {}
        data['name'] = str_rname.get();
        data['address'] = str_raddress.get();
        data['enabled'] = True;
        r = requests.post('http://' + str_server.get() + '/recipients', auth=(str_username.get(), str_password.get()), json={ 'name': data['name'], 'address': data['address'], 'enabled': data['enabled'] });
        retrieve_data();

def delete_address():
    name = lsvar_current_address.get();
    odata = db_addresses[name];
    r = requests.delete('http://' + str_server.get() + '/recipients/' + str(odata['rid']), auth=(str_username.get(), str_password.get()));
    str_rname.set("");
    str_raddress.set("");
    lsvar_current_address.set("");
    retrieve_data();

# GUI

# CONFIG PAGE
config_page = Frame(root, width=300, height=130, pady=20);

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
config_page_f1.grid(row=1,column=1,sticky=W);

config_page_f2 = Frame(config_page, padx=20);
button_saveSettings = Button(config_page_f2, text="Save Settings", command=save_settings);
button_saveSettings.grid(row=1,column=1);
button_retrieveData = Button(config_page_f2, text="Retrieve Data", command=retrieve_data);
button_retrieveData.grid(row=2,column=1);
config_page_f2.grid(row=1,column=2,sticky=E);

mw = ttk.Notebook(root, width=300, height=170);

# CLIENT PAGE
client_page = Frame(mw, padx=10, pady=10);

client_page_f1 = Frame(client_page);
ls_clients = OptionMenu(client_page_f1, lsvar_current_client, {"None"});
ls_clients.grid(row=1,column=1);
client_page_f1.grid(row=1,column=1);

# RECIPIENT PAGE
address_page = Frame(mw, padx=2, pady=2);

address_page_f1 = Frame(address_page, padx=4, pady=10);
ls_addresses = OptionMenu(address_page_f1, lsvar_current_address, {"None"});
lsvar_current_address.trace('w', dropdown_change_recipient);
ls_addresses.grid(row=1,column=2);
address_page_f1.grid(row=1,column=1,sticky=W);

address_page_f2 = Frame(address_page, padx=4, pady=10);
label_rname = Label(address_page_f2, text="Name");
input_rname = Entry(address_page_f2, textvariable=str_rname);
label_rname.grid(row=1,column=1);
input_rname.grid(row=1,column=2);

label_raddress = Label(address_page_f2, text="Address");
input_raddress = Entry(address_page_f2, textvariable=str_raddress);
label_raddress.grid(row=2,column=1);
input_raddress.grid(row=2,column=2);
address_page_f2.grid(row=2,column=1,sticky=W);

address_page_f3 = Frame(address_page, padx=4, pady=10);
button_saveAddress = Button(address_page_f3, text="Update", command=save_address);
button_saveAddress.grid(row=1,column=1);
button_newAddress = Button(address_page_f3, text="Save As New", command=save_address_as_new);
button_newAddress.grid(row=1,column=2);
button_deleteAddress = Button(address_page_f3, text="Delete", command=delete_address);
button_deleteAddress.grid(row=1,column=3);
address_page_f3.grid(row=3,column=1,sticky=W);

#mw.add(config_page, text="Config");
mw.add(client_page, text="Clients");
mw.add(address_page, text="Recipients");

mw.grid(row=1,column=1);
config_page.grid(row=2,column=1,sticky=W);

load_settings();
retrieve_data();

root.mainloop();
