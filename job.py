from lod_final_vkscrap.scrape import get_data
from lod_final_mltools.text_sentiment import get_text_sentiment
from lod_final_mltools.image_sentiment import make_predictions
from tqdm import tqdm
from shutil import rmtree
from os import mkdir
import wget
import json

# TODO pull IDs for scraping data from tarantool
IDs = [1, 280655896, 153378901]

try:
    rmtree("temp_img")
except:
    pass

ARTICLES_FILE = "articles.json"

mkdir("temp_img")

for id in IDs:
    articles = None
    with open(ARTICLES_FILE, 'r') as f:
        articles = json.loads(f.read())

    for i in range(len(articles['articles'])):
        articles['articles'][i]['sentiment'] = get_text_sentiment(articles['articles'][i]['text'])

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
        data['posts'][i]['sentiment'] = get_text_sentiment(data['posts'][i]['text']).value
    
    for i in range(len(data['mentions'])):
        data['mentions'][i]['sentiment'] = get_text_sentiment(data['mentions'][i]['text']).value

    for post in data['posts']:
        pass

    for mention in data['mentions']:
        pass

    # TODO push processed data to Tarantool
