from bs4 import BeautifulSoup
#import pip3, sys, requests
import csv
import string
import requests
from nltk.corpus import stopwords
from nltk import wordpunct_tokenize
import time
import random
import multiprocessing

#A-Z and 1
CAPITAL_LETTERS = string.ascii_uppercase + "1"
URL_FORMAT_STR = "https://www.letras.mus.br/%s/"
URL_ARTIST_FORMAT_STR = "http://www.letras.mus.br/letra/%s/artistas.html"


def convert_li_artist_tuple(li):
    href = li.a['href'] .strip('/')
    title = li.a.get_text()
    return href, title


def save_artists(artists):
    with open('artists.csv', 'w') as f:
        csv_writer = csv.writer(f)
        for row in artists:
            csv_writer.writerow(row)

# return a list containing (href, name)
def get_artists(letter):
    artists = []
    url = URL_ARTIST_FORMAT_STR % letter
    artists.extend(get_artist(url))
    artists = map(convert_li_artist_tuple, artists)
    return artists


def get_artist(url):
    page = requests.get(url)
    page_text = page.text
    bs = BeautifulSoup(page_text, "lxml")
    ul_item = bs.find_all('ul', 'cnt-list')[0]
    li_itens = ul_item.find_all('li')
    return li_itens


def get_musics_titles(artist):
    print(f"Getting musics for {artist}\n")
    url = URL_FORMAT_STR % artist
    page = requests.get(url)
    page_text = page.text
    bs = BeautifulSoup(page_text, "lxml")
    ul_item = bs.find_all('ul', 'cnt-list')[0]
    li_itens = ul_item.find_all('li')
    musics = list(map(convert_li_artist_tuple, li_itens))
    return musics


def _calculate_languages_ratios(text):
    languages_ratios = {}
    tokens = wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    # Compute per language included in nltk number of unique stopwords appearing in analyzed text
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        languages_ratios[language] = len(common_elements)  # language "score"

    return languages_ratios


def detect_language(lyric):
    ratios = _calculate_languages_ratios(lyric)
    most_rated_language = max(ratios, key=ratios.get)
    return most_rated_language


def get_genre_and_lyric(music):
    time.sleep(random.uniform(0, 1))
    url = URL_FORMAT_STR % music
    print(url)
    page = requests.get(url)
    page_text = page.text
    bs = BeautifulSoup(page_text, "lxml")
    genre = bs.find_all('span', itemprop="name")[1].text
    lyric = bs.find('div', 'cnt-letra').get_text(separator='\n')
    return genre, lyric

#def save_musics(musics):
#    musics = map(convert_li_artist_csv, musics)
#    with open('musics.txt', 'w') as f:
#        f.write('\n'.join(musics))


def get_by_letter(letter):
    for artist in get_artists(letter):
        musics = get_musics_titles(artist[0])
        if len(musics) > 0:
            lyric = get_genre_and_lyric(musics[0][0])
            if detect_language(lyric[1]) == 'portuguese':
                l = []
                for m in musics:
                    lyric = get_genre_and_lyric(m[0])
                    l.append(artist + lyric)
                with open(f'{artist[0]}.csv','w', encoding='utf-8') as f:
                    csv_writer = csv.writer(f)
                    for line in l:
                        csv_writer.writerow(line)

def main():
    #artists = get_artists()
    #save_artists(artists)
    #musics = get_musics_titles('chk-chk-chk')
    #save_musics(musics)
    #print(detect_language("hola amigo como estás"))

    '''for letter in list(CAPITAL_LETTERS):
        for artist in get_artists(letter):
            musics = get_musics_titles(artist[0])
            if len(musics) > 0:
                lyric = get_genre_and_lyric(musics[0][0])
                if detect_language(lyric[1]) == 'portuguese':
                    l = []
                    for m in musics:
                        lyric = get_genre_and_lyric(m[0])
                        l.append(artist + lyric)
                    with open(f'{artist[0]}.csv', 'w') as f:
                        csv_writer = csv.writer(f)
                        for line in l:
                            csv_writer.writerow(line)'''

    p = multiprocessing.Pool(multiprocessing.cpu_count())
    p.map(get_by_letter, list(CAPITAL_LETTERS))
    p.close()
    p.join()

if __name__ == "__main__":
    main()
