# -*- coding: utf-8 -*-
import sqlite3, Queue, re

def get_actors_from_film_string(film_id):
    return "SELECT actor_id FROM ActorFilm WHERE film_id = " + str(film_id) + ";"

def get_films_from_actor_string(actor_id):
    return "SELECT film_id FROM ActorFilm WHERE actor_id = " + str(actor_id) + " ORDER BY id DESC;"

def get_films_and_costars_string(actor_id):
    start = "SELECT ActorFilm.film_id, pair.actor_id FROM ActorFilm JOIN ActorFilm pair ON ActorFilm.film_id = pair.film_id WHERE ActorFilm.actor_id = "
    end = " GROUP BY pair.actor_id ORDER BY ActorFilm.id DESC;"
    return start + str(actor_id) + end

def get_link(cursor, actor_id, target_id):
    already_seen = set()
    queue = Queue.Queue()

    already_seen.add(actor_id)
    queue.put((actor_id,))

    while not queue.empty():
        current = queue.get()
        film_and_costars_string = get_films_and_costars_string(current[-1])
        cursor.execute(film_and_costars_string)
        links = cursor.fetchall()
        for link in links:
            if link[1] not in already_seen:
                new = current + link
                if link[1] == target_id:
                    return new
                queue.put(new)
                already_seen.add(link[1])

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

def find_actor(cursor, actor):
    con = sqlite3.connect('test.db')

    actor = '%' + re.sub('\W', '%', actor) + '%'

    print 'searching expression', actor
    cursor.execute("SELECT id, name FROM Actors WHERE name LIKE ?;", (actor,))
    result = cursor.fetchone()
    return result

def find_link(actor, target):
    con = sqlite3.connect('test.db')

    with con:
        cursor = con.cursor()
        actor_id = find_actor(cursor, actor)
        target_id = find_actor(cursor, target)

        if not actor_id or not target_id:
            return None

        link = get_link(cursor, actor_id[0], target_id[0])

        link = turn_link_to_names(cursor, link)

        return link

# link = find_link("Tom Cruise", "Cara")

# for i in link:
#     print i