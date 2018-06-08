import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json

root = Tk();
root.title("Godwatch Administrator")
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

str_ehost = StringVar();
str_ehost.set("");
str_eport = StringVar();
str_eport.set("");
str_euser = StringVar();
str_euser.set("");
str_epass = StringVar();
str_epass.set("");
int_esecure = IntVar();
int_esecure.set(1);
int_ereject = IntVar();
int_ereject.set(1);

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

            str_ehost.set(data['mailhost']);
            str_eport.set(data['mailport']);
            if data['securemail']:
                int_esecure.set(1);
            else:
                int_esecure.set(0);
            str_euser.set(data['mailuser']);
            str_epass.set(data['mailpass']);
            if data['mailRejectUnauthorized']:
                int_ereject.set(0);
            else:
                int_ereject.set(1);

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

def check_empty_config():
    if str_ehost.get() != "":
        if str_eport.get() != "":
            if str_euser.get() != "":
                if str_epass.get() != "":
                    return True;
                else:
                    return False;
            else:
                return False;
        else:
            return False;
    else:
        return False;

def save_config():
    if check_empty_config():

        newdata = {
            'mailhost': str_ehost.get(),
            'mailport': str_eport.get(),
            'mailuser': str_euser.get(),
            'mailpass': str_epass.get()
            }

        if int_esecure.get() == 1:
            newdata['securemail'] = False;
        else:
            newdata['securemail'] = True;

        if int_ereject.get() == 1:
            newdata['mailRejectUnauthorized'] = True;
        else:
            newdata['mailRejectUnauthorized'] = False;

        r = requests.put('http://' + str_server.get() + '/config/0', auth=(str_username.get(), str_password.get()), json=newdata);
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

label_server = Label(config_page_f1, text="Server: ");
input_server = Entry(config_page_f1, textvariable=str_server);
input_server.insert(0, "server:port");
label_server.grid(row=1,column=1,sticky=E);
input_server.grid(row=1,column=2,sticky=W);

label_username = Label(config_page_f1, text="Username: ");
input_username = Entry(config_page_f1, textvariable=str_username);
label_username.grid(row=2,column=1,sticky=E);
input_username.grid(row=2,column=2,sticky=W);

label_password = Label(config_page_f1, text="Password: ");
input_password = Entry(config_page_f1, textvariable=str_password, show="*");
label_password.grid(row=3,column=1,sticky=E);
input_password.grid(row=3,column=2,sticky=W);

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

label_cname = Label(client_page_f2, text="Name: ");
input_cname = Label(client_page_f2, textvariable=str_cname);
label_cname.grid(row=1,column=1,sticky=E);
input_cname.grid(row=1,column=2,sticky=W);

label_chash = Label(client_page_f2, text="Hash: ");
input_chash = Label(client_page_f2, textvariable=str_chash);
label_chash.grid(row=2,column=1,sticky=E);
input_chash.grid(row=2,column=2,sticky=W);

label_cinterval = Label(client_page_f2, text="Interval: ");
input_cinterval = Entry(client_page_f2, textvariable=str_cinterval);
label_cinterval.grid(row=3,column=1,sticky=E);
input_cinterval.grid(row=3,column=2,sticky=W);

#label_cdatereported = Label(client_page_f2, textvariable=str_cdatereported);
#label_cdatereported.grid(row=4,column=1);

client_page_f2.grid(row=2,column=1,sticky=W);

client_page_f3 = Frame(client_page, padx=4, pady=6);

button_saveClient = Button(client_page_f3, text="Update", command=save_client);
button_saveClient.grid(row=1,column=1);
button_deleteClient = Button(client_page_f3, text="Delete", command=delete_client);
button_deleteClient.grid(row=1,column=2);

client_page_f3.grid(row=3,column=1,sticky=W);

# RECIPIENT PAGE
address_page = Frame(mw, padx=2, pady=2);

address_page_f1 = Frame(address_page, padx=4, pady=10);
ls_addresses = OptionMenu(address_page_f1, lsvar_current_address, {"None"});
lsvar_current_address.trace('w', dropdown_change_recipient);
ls_addresses.grid(row=1,column=2);
address_page_f1.grid(row=1,column=1,sticky=W);

address_page_f2 = Frame(address_page, padx=4, pady=10);

label_rname = Label(address_page_f2, text="Name: ");
input_rname = Entry(address_page_f2, textvariable=str_rname);
label_rname.grid(row=1,column=1,sticky=E);
input_rname.grid(row=1,column=2,sticky=W);

label_raddress = Label(address_page_f2, text="Address: ");
input_raddress = Entry(address_page_f2, textvariable=str_raddress);
label_raddress.grid(row=2,column=1,sticky=E);
input_raddress.grid(row=2,column=2,sticky=W);

label_renabled = Label(address_page_f2, text="Enabled: ");
input_renabled = Checkbutton(address_page_f2, variable=int_renabled);
label_renabled.grid(row=3,column=1,sticky=E);
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

# SERVER PAGE
server_page = Frame(mw, padx=2, pady=2);

server_page_f1 = Frame(server_page, padx=4, pady=10);

label_ehost = Label(server_page_f1, text="Host: ");
input_ehost = Entry(server_page_f1, textvariable=str_ehost);
label_ehost.grid(row=1,column=1,sticky=E);
input_ehost.grid(row=1,column=2,sticky=W);

label_eport = Label(server_page_f1, text="Port: ");
input_eport = Entry(server_page_f1, textvariable=str_eport);
label_eport.grid(row=2,column=1,sticky=E);
input_eport.grid(row=2,column=2,sticky=W);

label_esecure = Label(server_page_f1, text="Secure: ");
label_esecure.grid(row=3,column=1,sticky=E);

server_bool_page = Frame(server_page_f1);

input_esecure = Checkbutton(server_bool_page, variable=int_esecure);
input_esecure.grid(row=1,column=2,sticky=W);

label_ereject = Label(server_bool_page, text="Ignore SSL: ");
input_ereject = Checkbutton(server_bool_page, variable=int_ereject);
label_ereject.grid(row=1,column=3,sticky=E);
input_ereject.grid(row=1,column=4,sticky=E);

server_bool_page.grid(row=3,column=2);

label_euser = Label(server_page_f1, text="User: ");
input_euser = Entry(server_page_f1, textvariable=str_euser);
label_euser.grid(row=4,column=1,sticky=E);
input_euser.grid(row=4,column=2,sticky=W);

label_epass = Label(server_page_f1, text="Pass: ");
input_epass = Entry(server_page_f1, textvariable=str_epass, show="*");
label_epass.grid(row=5,column=1,sticky=E);
input_epass.grid(row=5,column=2,sticky=W);

server_page_f1.grid(row=2,column=1,sticky=W);

server_page_f2 = Frame(server_page, padx=4, pady=11);

button_saveConfig = Button(server_page_f2, text="Update", command=save_config);
button_saveConfig.grid(row=1,column=1,sticky=W);

server_page_f2.grid(row=3,column=1,sticky=W);

#mw.add(config_page, text="Config");
mw.add(client_page, text="Clients");
mw.add(address_page, text="Recipients");
mw.add(server_page, text="Configuration");

mw.grid(row=1,column=1);
config_page.grid(row=2,column=1,sticky=W);

load_settings();
retrieve_data();

root.mainloop();
