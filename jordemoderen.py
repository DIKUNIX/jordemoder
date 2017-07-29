# Webgrænsefladen.
#
# Kør kun det her entrådet.

import os.path
import subprocess
import html
from email.mime.text import MIMEText
import smtplib
import socket
import time
import csv
import random

from flask import Flask, request

from nisselib import *


# DATABASE.

# Funktioner.

def read_rows(csv_path, func):
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if func(*row):
                yield row

def read_row(csv_path, func):
    rows = list(read_rows(csv_path, func))
    if len(rows) == 1:
        return rows[0]

def write_rows(csv_path, rows):
    existing = read_rows(csv_path, lambda *row: True)
    with open(csv_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(list(existing) + list(rows))

def write_row(csv_path, row):
    write_rows(csv_path, [row])

def remove_rows(csv_path, func):
    write_rows(csv_path, read_rows(csv_path, lambda *row: not func(*row)))

# Stier.
igang_csv = '/home/jordemoder/midlertidige-oprettelser.csv'
endelig_csv = '/home/jordemoder/brugere.csv'

if not os.path.isfile(igang_csv):
    with open(igang_csv, 'w', encoding='utf-8') as f:
        f.write('')
if not os.path.isfile(endelig_csv):
    with open(endelig_csv, 'w', encoding='utf-8') as f:
        f.write('')

# Fjern gamle oprettelser.
remove_rows(igang_csv, lambda _0, _1, _2, _3, tid:
            time.time() - float(tid) < 60.0 * 60.0)


# WSGI.

app = Flask(__name__)

@app.route('/ny-bruger/', methods=['GET'])
def ny_bruger_get():
    aktiveringskode = request.args.get('aktivering')
    if aktiveringskode is None:
        return ny_bruger_vis()
    else:
        navn = request.args.get('navn')
        return ny_bruger_aktiver(aktiveringskode, navn)

@app.route('/ny-bruger/', methods=['POST'])
def ny_bruger_post():
    return ny_bruger_arbejd()


# SIDER.

# Vis formular.
def ny_bruger_vis():
    return frafil('ny-bruger.html').format(
        fejlbesked='', navn='', emailadresse='', sshkey='')

# Arbejd med formulardata.
def ny_bruger_arbejd():
    data = request.form
    navn = data['navn']
    emailadresse = data['emailadresse']
    sshkey = data['sshkey'].strip()

    if not is_valid_username(navn):
        return frafil('ny-bruger.html').format(
            fejlbesked=fejl_html('Dit brugernavn skal matche det regulære udtryk {}.'.format(VALID_USERNAMES_REGEX)),
            navn='',
            emailadresse=html.escape(emailadresse),
            sshkey=html.escape(sshkey))

    if brugernavn_er_i_brug(navn) or brugernavn_er_under_oprettelse(navn):
        return frafil('ny-bruger.html').format(
            fejlbesked=fejl_html('Brugernavnet "{}" er allerede i brug.'.format(navn)),
            navn='',
            emailadresse=html.escape(emailadresse),
            sshkey=html.escape(sshkey))

    if not er_god_emailadresse(emailadresse):
        return frafil('ny-bruger.html').format(
            fejlbesked=fejl_html('Din emailadresse skal være en ku.dk-emailadresse.'),
            navn=html.escape(navn),
            emailadresse='',
            sshkey=html.escape(sshkey))

    if not is_valid_ssh_key(sshkey):
        return frafil('ny-bruger.html').format(
            fejlbesked=fejl_html('Din offentlige ssh-nøgle ser forkert ud.'),
            navn=html.escape(navn),
            emailadresse=html.escape(emailadresse),
            sshkey='')

    aktiveringskode = ''.join([chr(random.randint(ord('a'), ord('z')))
                               for i in range(9)])
    write_row(igang_csv, (navn, emailadresse, sshkey,
                          aktiveringskode, str(time.time())))
    aktiveringslink = 'http://dikunix.dk/ny-bruger/?navn={}&aktivering={}'.format(
        navn, aktiveringskode)

    emailbesked = frafil('ny-bruger-elektropost.txt').format(
        navn=navn, link=aktiveringslink)
    send_elektropost(emailadresse,
                     'Ny bruger på dikunix.dk',
                     emailbesked)

    return frafil('email-sendt.html').format(
        navn=navn, emailadresse=emailadresse)

# Prøv at aktivere en bruger der har fået et emaillink.
def ny_bruger_aktiver(aktiveringskode, navn):
    row = read_row(igang_csv, lambda navn1, _0, _1, aktiveringskode1, _2:
                   navn1 == navn and aktiveringskode1 == aktiveringskode)
    if row is not None:
        navn, emailadresse, sshkey, _, _ = row
        try:
            opret_bruger(navn, sshkey, emailadresse)
        except socket.error as msg:
            return frafil('fejl-under-oprettelse.html').format(
                fejlbesked=fejl_html('Nissefejl: {}'.format(msg)))
        else:
            return frafil('bruger-oprettet.html').format(
                navn=navn)
    else:
        return frafil('fejl-under-oprettelse.html').format(
            fejlbesked=fejl_html('Der var noget galt med aktiveringskoden.'))


# VÆRKTØJER.

def frafil(sti):
    with open(os.path.join('data', sti), encoding='utf-8') as f:
        return f.read()

def fejl_html(s):
    return '<p style="color: maroon">Fejl: {}</p>'.format(html.escape(s))

def brugernavn_er_i_brug(navn):
    return navn in subprocess.run(
        'cut -d: -f1 < /etc/passwd',
        shell=True, stdout=subprocess.PIPE).stdout.decode().rstrip().split('\n')

def brugernavn_er_under_oprettelse(navn):
    row = read_row(igang_csv, lambda navn1, _0, _1, _2, _3: navn1 == navn)
    return row is not None

def er_god_emailadresse(emailadresse):
    return (
        emailadresse.endswith('@alumni.ku.dk') or
        emailadresse.endswith('@ku.dk') or
        emailadresse.endswith('@localhost') # til debugging
    )

def send_elektropost(modtageradresse, emnefelt, besked):
    msg = MIMEText(besked)
    msg['Subject'] = emnefelt
    msg['From'] = 'jordemoder-no-reply@dikunix.dk'
    msg['To'] = modtageradresse
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def opret_bruger(navn, sshkey, emailadresse):
    # Send beskeden til nissen.
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/home/jordemoder/brugernissen.socket')
    fd = s.makefile(mode='rw')
    fd.write(navn + '\n' + sshkey + '\n')
    fd.flush()

    # Fjern fra midlertidig-databasen.
    remove_rows(igang_csv, lambda navn1, _0, _1, _2, _3: navn1 == navn)

    # Gem navn-emailadresse-parret.
    write_row(endelig_csv, (navn, emailadresse))
