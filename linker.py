# -*- coding: utf-8 -*-
import sqlite3, Queue

con = sqlite3.connect('test.db')

already_seen = set()
queue = Queue.Queue()


def get_actors_from_films_string(films):
    s = "SELECT DISTINCT actor_id FROM ActorFilm WHERE film_id IN ("
    for film in films:
        s += str(film[0]) + ', '
    return s[:-2] + ');'

def get_films_from_actor_string(actor_id):
    return "SELECT film_id FROM ActorFilm WHERE actor_id = " + str(actor_id) + ";"

def get_costars(cursor, actor_id):
    cursor.execute(get_films_from_actor_string(actor_id))
    films = cursor.fetchall()
    actors_string = get_actors_from_films_string(films)
    cursor.execute(actors_string)
    return cursor.fetchall()

def get_colleagues(cursor, actor_id, depth):
    already_seen.add(actor_id)
    queue.put((actor_id,))

    while depth > 0:
        current = queue.get()
        costars = get_costars(cursor, current[-1])
        for costar in costars:
            if costar[0] not in already_seen:
                new = current + costar
                queue.put(new)
                already_seen.add(costar[0])
        depth -= 1



with con:
    cursor = con.cursor()
    cursor.execute("SELECT id FROM Actors WHERE name = 'Arnold Schwarzenegger';")
    actor_id = cursor.fetchone()[0]
    get_colleagues(cursor, actor_id, 50)

    while not queue.empty():
        our_string = ''
        item = queue.get()
        for i in item:
            cursor.execute("SELECT name FROM Actors WHERE id = ?;", (i,))
            our_string += ' - ' + repr(cursor.fetchone()[0])
        print our_string