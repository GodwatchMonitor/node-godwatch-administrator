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
int_renabled = IntVar();
int_renabled.set(1);

str_cname = StringVar();
str_cname.set("");
str_chash = StringVar();
str_chash.set("");
str_cinterval = StringVar();
str_cinterval.set("");
str_cipaddr = StringVar();
str_cipaddr.set("");
int_cenabled = IntVar();
int_cenabled.set(1);
str_cdatereported = StringVar();
str_cdatereported.set("");

lsvar_current_address = StringVar();
lsvar_current_client = StringVar();

db_addresses = {};
db_clients = {};

makemodal = (len(sys.argv) > 1);

# METHODS
def reset_stringvars():
    str_rname.set("");
    str_raddress.set("");
    int_renabled.set(1);

    str_cname.set("");
    str_chash.set("");
    str_cinterval.set("");
    str_cipaddr.set("");
    int_cenabled.set(1);
    str_cdatereported.set("");

def retrieve_data():

    reset_stringvars();

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
                    rcd = json.loads(rc.text);
                    if not rcd is None:
                        ls_clients['menu'].add_command(label=rcd['name'], command=tk._setit(lsvar_current_client, rcd['name']));
                        db_clients[rcd['name']] = rcd;
                        lsvar_current_client.set(rcd['name']);

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
                        lsvar_current_address.set(rrd['name']);

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
        if data['enabled']:
            int_renabled.set(1);
        else:
            int_renabled.set(0);

def dropdown_change_client(*args):
    name = lsvar_current_client.get();
    if name != "" and name != "{'None'}":
        data = db_clients[name];
        str_cname.set(data['name']);
        str_cipaddr.set(data['ipaddr']);
        str_cinterval.set(data['interval']);
        str_chash.set(data['hash']);
        str_cdatereported.set(data['datereported']);
        #if data['enabled']:
        #    int_cenabled.set(1);
        #else:
        #    int_cenabled.set(0);

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n');
    settings_file.close();

def check_empty_address():
    if str_rname.get() != "":
        if str_raddress.get() != "":
            return True;
        else:
            return False;
    else:
        return False;

def save_address():
    if check_empty_address():
        name = lsvar_current_address.get();
        if name != "" and name != "{'None'}":
            odata = db_addresses[name];
            data = {}
            data['name'] = str_rname.get();
            data['address'] = str_raddress.get();
            if int_renabled.get() == 1:
                data['enabled'] = True;
            else:
                data['enabled'] = False;
            r = requests.put('http://' + str_server.get() + '/recipients/' + str(odata['rid']), auth=(str_username.get(), str_password.get()), json={ 'name': data['name'], 'address': data['address'], 'enabled': data['enabled'] });
            retrieve_data();
        else:
            save_address_as_new();

def save_address_as_new():
    if check_empty_address():
        data = {}
        data['name'] = str_rname.get();
        data['address'] = str_raddress.get();
        if int_renabled.get() == 1:
            data['enabled'] = True;
        else:
            data['enabled'] = False;
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

def check_empty_client():
    if str_cname.get() != "":
        if str_chash.get() != "":
            if str_cinterval.get() != "":
                return True;
            else:
                return False;
        else:
            return False;
    else:
        return False;

def save_client():
    if check_empty_client():
        name = lsvar_current_client.get();
        if name != "" and name != "{'None'}":
            odata = db_clients[name];
            data = {}
            data['name'] = str_cname.get();
            data['interval'] = str_cinterval.get();
            data['hash'] = str_chash.get();
            if int_cenabled.get() == 1:
                data['enabled'] = True;
            else:
                data['enabled'] = False;
            r = requests.put('http://' + str_server.get() + '/clients/' + str(odata['cid']), auth=(str_username.get(), str_password.get()), json={ 'name': data['name'], 'interval': data['interval'], 'hash': data['hash'], 'enabled': data['enabled'] });
            retrieve_data();
        else:
            save_client_as_new();

def save_client_as_new():
    if check_empty_client():
        data = {}
        data['name'] = str_cname.get();
        data['interval'] = str_cinterval.get();
        data['hash'] = str_chash.get();
        if int_cenabled.get() == 1:
            data['enabled'] = True;
        else:
            data['enabled'] = False;
        r = requests.post('http://' + str_server.get() + '/clients', auth=(str_username.get(), str_password.get()), json={ 'name': data['name'], 'interval': data['interval'], 'hash': data['hash'], 'enabled': data['enabled'] });
        retrieve_data();

def delete_client():
    name = lsvar_current_client.get();
    odata = db_clients[name];
    r = requests.delete('http://' + str_server.get() + '/clients/' + str(odata['cid']), auth=(str_username.get(), str_password.get()));
    str_cname.set("");
    str_cipaddr.set("");
    lsvar_current_client.set("");
    retrieve_data();

# GUI

# CONFIG PAGE
config_page = Frame(root, width=300, height=110, pady=10);

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
client_page = Frame(mw, padx=2, pady=2);

client_page_f1 = Frame(client_page, padx=4, pady=10);
ls_clients = OptionMenu(client_page_f1, lsvar_current_client, {"None"});
lsvar_current_client.trace('w', dropdown_change_client);
label_cipaddr = Label(client_page_f1, textvariable=str_cipaddr);
ls_clients.grid(row=1,column=1);
label_cipaddr.grid(row=1,column=2);
client_page_f1.grid(row=1,column=1,sticky=W);

client_page_f2 = Frame(client_page, padx=4, pady=10);

label_cname = Label(client_page_f2, text="Name");
input_cname = Entry(client_page_f2, textvariable=str_cname);
label_cname.grid(row=1,column=1);
input_cname.grid(row=1,column=2);

label_chash = Label(client_page_f2, text="Hash");
input_chash = Entry(client_page_f2, textvariable=str_chash);
label_chash.grid(row=2,column=1);
input_chash.grid(row=2,column=2);

label_cinterval = Label(client_page_f2, text="Interval");
input_cinterval = Entry(client_page_f2, textvariable=str_cinterval);
label_cinterval.grid(row=3,column=1);
input_cinterval.grid(row=3,column=2);

#label_cdatereported = Label(client_page_f2, textvariable=str_cdatereported);
#label_cdatereported.grid(row=4,column=1);

client_page_f2.grid(row=2,column=1,sticky=W);

client_page_f3 = Frame(client_page, padx=4, pady=6);

button_saveClient = Button(client_page_f3, text="Update", command=save_client);
button_saveClient.grid(row=1,column=1);
button_newClient = Button(client_page_f3, text="Save As New", command=save_client_as_new);
button_newClient.grid(row=1,column=2);
button_deleteClient = Button(client_page_f3, text="Delete", command=delete_client);
button_deleteClient.grid(row=1,column=3);

client_page_f3.grid(row=3,column=1,sticky=W);

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

label_renabled = Label(address_page_f2, text="Enabled");
input_renabled = Checkbutton(address_page_f2, variable=int_renabled);
label_renabled.grid(row=3,column=1);
input_renabled.grid(row=3,column=2,sticky=W);

address_page_f2.grid(row=2,column=1,sticky=W);

address_page_f3 = Frame(address_page, padx=4, pady=2);
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
