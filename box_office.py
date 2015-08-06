# -*- coding: utf-8 -*-


import requests
import sqlite3, sys

url = 'http://www.imdb.com/search/name?gender=male,female&start='
base_url = 'http://www.imdb.com/'

page_number = 501

actors = []

class Film:
    def __init__(self, n, l):
        self.name = n
        self.link = l

    def __str__(self):
        return self.name + ' ' + self.link

class Actor:
    def __init__(self, n, l):
        self.name = n
        self.link = l
        self.films = []

    def __str__(self):
        fs = ''
        for f in self.films:
            fs += str(f) + ' '
        return self.name + ' ' + self.link + ' ' + fs

def get_url(type_of_url, identifier):
    return base_url + type_of_url + identifier + '/'

def get_credits(text):
    actor_actress = text.find('<a name="actress">')
    if actor_actress == -1:
        actor_actress = text.find('<a name="actor">')
    if actor_actress == -1:
        return 0
    credit_start = text.find('(', actor_actress)
    credit_end = text.find(' ', credit_start)
    return int(text[credit_start+1:credit_end])

def get_films(text, credits):
    films = []

    find = text.find('<span class="year_column">')

    for i in range(credits):
        find = text.find('year_column', find)
        find = text.find('<a href=', find)
        link_start = text.find('tt', find)
        link_end = text.find('/?', link_start)
        link = text[link_start:link_end]
        find = text.find('>', find)
        end = text.find('</a>', find)
        bracket = text.find('(', end)
        if bracket - end < 10:
            continue
        title = text[find+1:end]
        film = Film(title, link)
        films.append(film)
    return films

def get_actor(name, address):
    url = get_url('/name/', address)
    s = requests.get(url)
    actor_text = s.text

    credits = get_credits(actor_text)

    if credits == 0:
        return

    films = get_films(actor_text, credits)

    if len(films) < 1:
        return

    currect_actor = Actor(name, address)

    currect_actor.films = films

    print currect_actor.name
    print
    actors.append(currect_actor)

bo_url_start = 'http://www.boxofficemojo.com/people/?view=Actor&pagenum='
bo_url_end = '&sort=sumgross&order=DESC&&p=.htm'

page = 1

targets = set()

while page < 10:
    r = requests.get(bo_url_start + str(page) + bo_url_end)
    text = r.text

    index = text.find('<td><font size="2"><a href=')

    while index != -1:
        start = text.find('<b>', index)
        end = text.find('</b>', start)
        name = text[start+3:end]
        targets.add(name)
        index = text.find('<td><font size="2"><a href=', start)

    page += 1


while page_number < 1000:
    r = requests.get(url + str(page_number))

    text = r.text

    index = text.find('<td class="name">', 0)


    while index != -1:
        start = text.find('<a href=', index)
        end = text.find('</a>', start)
        actor = text[start:end]
        name = actor[actor.find('>')+1:]
        if name in targets:
            print 'found', name
            targets.remove(name)
            address_start = actor.find('nm')
            address_end = actor.find('/', address_start)
            address = actor[address_start:address_end]
            get_actor(name, address)
        index = text.find('<td class="name">', index+1)
        # index = -1


    print
    page_number += 50

print
print 'database time!'
print

try:
    con = sqlite3.connect('test.db')

    cur = con.cursor()

    for actor in actors:
        print actor.name
        cur.execute("SELECT id FROM Actors WHERE link = ?;", (actor.link,))
        actor_id = cur.fetchone()
        if actor_id:
            actor_id = actor_id[0]
        else:
            cur.execute("INSERT INTO Actors (name, link) VALUES(?, ?);", (actor.name, actor.link))
            actor_id = cur.lastrowid
        for film in actor.films:
            cur.execute("SELECT id FROM Films WHERE link = ?;", (film.link,))
            film_id = cur.fetchone()
            if film_id:
                film_id = film_id[0]
            else:
                cur.execute("INSERT INTO Films (name, link) VALUES(?, ?);", (film.name, film.link))
                film_id = cur.lastrowid
            cur.execute("SELECT id FROM ActorFilm WHERE (actor_id = ? AND film_id = ?);", (actor_id, film_id))
            actor_film_id = cur.fetchone()
            if not actor_film_id:
                cur.execute("INSERT INTO ActorFilm (actor_id, film_id) VALUES(?, ?);", (actor_id, film_id))

    con.commit()

except sqlite3.Error, e:
    print e.args[0]
    sys.exit(1)

finally:
    if con:
        con.close()