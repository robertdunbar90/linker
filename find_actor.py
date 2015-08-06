# -*- coding: utf-8 -*-


import requests

url = 'http://www.imdb.com/search/name?gender=male,female&start='

page_number = 501

target_name = 'Sigourney Weaver'

cont = True


while page_number < 1000  and cont:
    r = requests.get(url + str(page_number))

    text = r.text

    index = text.find('<td class="name">', 0)

    i = 0

    while index != -1 and cont:
        start = text.find('<a href=', index)
        end = text.find('</a>', start)
        actor = text[start:end]
        name = actor[actor.find('>')+1:]

        if name == target_name:
            cont = False
            print name, page_number + i


        i += 1
        index = text.find('<td class="name">', index+1)
        # index = -1


    print
    page_number += 50