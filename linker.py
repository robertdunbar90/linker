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

def get_actors_from_film_string(film_id):
    return "SELECT actor_id FROM ActorFilm WHERE film_id = " + str(film_id) + ";"

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
        film_string = get_films_from_actor_string(current[-1])
        cursor.execute(film_string)
        films = cursor.fetchall()
        for film in films:
            actor_string = get_actors_from_film_string(film[0])
            cursor.execute(actor_string)
            actors = cursor.fetchall()
            for actor in actors:
                if actor[0] not in already_seen:
                    new = current + film + actor
                    queue.put(new)
                    already_seen.add(actor[0])
        depth -= 1

def get_link(cursor, actor_id, target_id):
    already_seen.add(actor_id)
    queue.put((actor_id,))

    while not queue.empty():
        current = queue.get()
        film_string = get_films_from_actor_string(current[-1])
        cursor.execute(film_string)
        films = cursor.fetchall()
        for film in films:
            actor_string = get_actors_from_film_string(film[0])
            cursor.execute(actor_string)
            actors = cursor.fetchall()
            for actor in actors:
                if actor[0] not in already_seen:
                    new = current + film + actor
                    if actor[0] == target_id:
                        return new
                    queue.put(new)
                    already_seen.add(actor[0])



with con:
    cursor = con.cursor()
    cursor.execute("SELECT id FROM Actors WHERE name = 'Benedict Cumberbatch';")
    actor_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM Actors WHERE name = 'Quentin Tarantino';")
    target_id = cursor.fetchone()[0]
    # get_colleagues(cursor, actor_id, 15)

    link = get_link(cursor, actor_id, target_id)

    if link == None:
        print 'Fail!'
    else:
        for i, v in enumerate(link):
            if i % 2 == 0:  
                cursor.execute("SELECT name FROM Actors WHERE id = ?;", (v,))
            else:
                cursor.execute("SELECT name FROM Films WHERE id = ?;", (v,))
            print cursor.fetchone()[0]

    # while not queue.empty():
    #     our_string = ''
    #     item = queue.get()
    #     for index, value in enumerate(item):
    #         if index % 2 == 0:
    #             cursor.execute("SELECT name FROM Actors WHERE id = ?;", (value,))
    #         else:
    #             cursor.execute("SELECT name FROM Films WHERE id = ?;", (value,))
    #         our_string += ' - ' + repr(cursor.fetchone()[0])
    #     print our_string