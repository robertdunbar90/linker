# -*- coding: utf-8 -*-
import sqlite3, Queue

def get_actors_from_film_string(film_id):
    return "SELECT actor_id FROM ActorFilm WHERE film_id = " + str(film_id) + ";"

def get_films_from_actor_string(actor_id):
    return "SELECT film_id FROM ActorFilm WHERE actor_id = " + str(actor_id) + ";"

def get_link(cursor, actor_id, target_id):
    already_seen = set()
    queue = Queue.Queue()
    
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

def get_actor_from_id(cursor, actor_id):
    cursor.execute("SELECT name FROM Actors WHERE id = ?;", (actor_id,))
    return cursor.fetchone()

def get_film_from_id(cursor, film_id):
    cursor.execute("SELECT name FROM Films WHERE id = ?;", (film_id,))
    return cursor.fetchone()

def turn_link_to_names(cursor, link):
    results = []
    for i, item in enumerate(link):
        if i%2 == 0:
            results.append(get_actor_from_id(cursor, item)[0])
        else:
            results.append(get_film_from_id(cursor, item)[0])
    return results

def find_link(actor, target):
    con = sqlite3.connect('test.db')

    with con:
        cursor = con.cursor()
        cursor.execute("SELECT id FROM Actors WHERE name = ?;", (actor,))
        actor_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM Actors WHERE name = ?;", (target,))
        target_id = cursor.fetchone()[0]

        link = get_link(cursor, actor_id, target_id)

        link = turn_link_to_names(cursor, link)

        return link

def find_actor(actor):
    con = sqlite3.connect('test.db')

    actor = '%' + '%'.join(actor.split()) + '%'

    with con:
        cursor = con.cursor()
        print actor
        cursor.execute("SELECT id, name FROM Actors WHERE name LIKE ?;", (actor,))
        result = cursor.fetchall()
        return result