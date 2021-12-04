from lod_final_vkscrap.scrape import get_data
from lod_final_mltools.text_sentiment import get_text_sentiment
from lod_final_mltools.image_sentiment import make_predictions
from tqdm import tqdm
from shutil import rmtree
from os import mkdir
from datetime import datetime
import wget
import json
import tarantool
from credentials import TARANTOOL_IP, TARANTOOL_PORT

db = tarantool.Connection(TARANTOOL_IP, TARANTOOL_PORT)


def new_id(space):
    entries = db.select(space)
    return len(entries) + 1


def vk_id_to_tarantool_id(vkid):
    results = list(db.select('vk', (vkid,), index='secondary'))
    if len(results) == 0:
        return None

    return results[0][2]


def print_time(t):
    datetime.utcfromtimestamp(t).strftime("%Y/%m/%d")


ARTICLES_FILE = "articles.json"

articles = None
with open(ARTICLES_FILE, 'r') as f:
    articles = json.loads(f.read())

for i in range(len(articles['articles'])):
    articles['articles'][i]['sentiment'] = get_text_sentiment(
        articles['articles'][i]['text']).value

for article in articles['articles']:
    ids = list(db.select(
        'user',
        (article['name'], article['surname'], article['patronymic']),
        index='secondary'))

    if len(ids) == 0:
        continue

    user_id = ids[0][1]

    id = new_id('mention')

    db.insert('mention', (id, user_id, article['sentiment'], print_time(
        datetime.now().timestamp()), article['link'], article['text'], ''))

try:
    rmtree("temp_img")
except:
    pass

mkdir("temp_img")

# TODO pull IDs for scraping data from tarantool
IDs = [1, 280655896, 153378901]

for id in IDs:
    data = get_data(id)  # Collect data from VK

    image_paths = list()
    for i in range(len(data['photos'])):
        photo = data['photos'][i]
        image_paths.append('temp_img/' + wget.detect_filename(photo['link']))
        wget.download(photo['link'], out="temp_img/")

    image_predictions = make_predictions(image_paths, batch_size=8)

    for i in range(len(data['photos'])):
        data['photos'][i]['sentiment'] = image_predictions[i].value

    for i in range(len(data['posts'])):
        data['posts'][i]['sentiment'] = get_text_sentiment(
            data['posts'][i]['text']).value

    for i in range(len(data['mentions'])):
        data['mentions'][i]['sentiment'] = get_text_sentiment(
            data['mentions'][i]['text']).value

    # Publication
    for photo in data['photos']:
        id = new_id('publication')
        user_id = vk_id_to_tarantool_id(photo['user'])
        if user_id is None:
            continue

        db.insert('publication', (id, user_id, 1, photo['sentiment'], print_time(
            photo['date']), photo['link'], ''))

    for post in data['posts']:
        # Publication types:
        # 1 - Photo
        # 2 - Post
        # 3 - Comments
        id = new_id('publication')
        user_id = vk_id_to_tarantool_id(post['user'])
        if user_id is None:
            continue

        db.insert('publication', (id, user_id, 2, post['sentiment'], print_time(
            post['date']), post['link'], post['text']))

    # Mention
    for mention in data['mentions']:
        id = new_id('mention')
        user_id = vk_id_to_tarantool_id(mention['user'])
        if user_id is None:
            continue

        db.insert('mention', (id, user_id, mention['sentiment'], print_time(
            mention['date']), mention['link'], mention['text'], mention['mentioned_by']))
