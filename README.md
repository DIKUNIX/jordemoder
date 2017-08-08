# multiuser

Kravlegård og legeplads for studerende.


## Afhængigheder

```
pkg_add py3-pip
pip install -r requirements.txt
```


## Opsætning

Hav `include "/home/jordemoder/fastcgi/httpd.conf"` i `/etc/httpd.conf`
i `server "dikunix.dk"`-gruppen.

Sørg for at `fastcgi/start.sh` køres ved boot af jordemoder.

Sørg for at `brugernissen.py` køres ved boot af root.

Hertil kan du bruge `crontab`. `-u` argumentet kan bruges til at skedulere
opgaver for en givet bruger. `-l` argumentet kan bruges til at liste hvilke
opgaver der er registreret. `-e` argumentet kan bruges til at modificere
opgavelisten. F.eks., for `jordemoder` skal der stå:

```
$ crontab -u jordemoder -l
...
@reboot /home/jordemoder/multiuser/fastcgi/start.sh
...
```

Ligeledes for `root` skal der stå:

```
$ crontab -u root -l
...
@reboot /home/jordemoder/multiuser/brugernissen.py
...
```

Sørg for at kunne sende emails fra serveren.

Nogle OpenBSD-indstillinger skal drejes lidt for at jordemoder har nok
resurser til at køre uwsgi; se
http://www.skipfeed.com/2017/06/uwsgi-on-openbsd.html


## Resultater

Fastcgi-log i `/home/jordemoder/uwsgi.log`.

Når en bruger oprettes, gemmes brugernavnet med dets tilhørende email i
`/home/jordemoder/brugere.csv`.

## Afprøvning

Der er lidt afprøvning nede i `./tests/`. Du kan køre afprøvning således:

```
$ python3 -m pytest ./tests/
```
