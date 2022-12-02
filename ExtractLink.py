from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
import nltk
from newspaper import Article
from PIL import Image, ImageFont, ImageDraw
import translators as ts
import schedule
import time
import tweepy
import keys
OldUrl = ""

def Run():
    global OldUrl
    print(OldUrl)
    def links():
        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get("https://cryptodaily.co.uk/")
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)

        for link in soup.find_all('a', class_="wide-breakin-link", href=True):
            NewUrl = link['href']
        return NewUrl

    NewUrl = links()

    if NewUrl != OldUrl:
        OldUrl = NewUrl
        url = OldUrl

        article = Article(url)

        article.download()  # Downloads the link’s HTML content
        article.parse()  # Parse the article
        nltk.download('punkt')  # 1 time download of the sentence tokenizer
        article.nlp()  # Keyword extraction wrapper

        print(article.title)

        sum = article.summary

        print(sum)

        sum = sum.replace('“', "'")
        sum = sum.replace('”', "'")
        message = sum

        def text_wrap(text, font, writing, max_width, max_height):
            time.sleep(1)
            lines = [[]]
            words = text.split()
            for word in words:
                # try putting this word in last line then measure
                lines[-1].append(word)
                (w, h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
                if w > max_width:  # too wide
                    # take it back out, put it on the next line, then measure again
                    lines.append([lines[-1].pop()])
                    (w, h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
                    if h > max_height:  # too high now, cannot fit this word in, so take out - add ellipses
                        lines.pop()
                        # try adding ellipses to last word fitting (i.e. without a space)
                        lines[-1][-1] += '...'
                        # keep checking that this doesn't make the textbox too wide,
                        # if so, cycle through previous words until the ellipses can fit
                        while writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)[
                            0] > max_width:
                            lines[-1].pop()
                            if lines[-1]:
                                lines[-1][-1] += '...'
                            else:
                                lines[-1].append('...')
                        break
            return '\n'.join([' '.join(line) for line in lines])

        bg = Image.open('Plantilla.png')
        ws = Image.open('Plantilla2.png')

        writing = ImageDraw.Draw(bg)

        title = article.title
        description = message
        Translated = ts.google(description, from_language='en', to_language='es')
        TranslatedT = ts.deepl(title, from_language='en', to_language='es')

        title_font = ImageFont.truetype("arial.ttf", size=30)
        desc_font = ImageFont.truetype("arial.ttf", size=25)

        description_wrapped = text_wrap(Translated, desc_font, writing, 700, 700)

        title_wrapped = text_wrap(TranslatedT, title_font, writing, 700, 700)
        # write title and description
        writing.text((200, 190), title_wrapped, font=title_font, fill=(8, 7, 7))

        writing.text((200, 300), description_wrapped, font=desc_font, fill=(8, 7, 7))

        out = Image.alpha_composite(bg, ws)
        out.save('output.png')

        def api():
            auth = tweepy.OAuthHandler(keys.api_key, keys.api_secret)
            auth.set_access_token(keys.access_token, keys.access_token_secret)

            return tweepy.API(auth)

        def tweet(api: tweepy.API, message: str, image_path=None):
            if image_path:
                api.update_status_with_media(message, image_path)
            else:
                api.update_status(message)

            print('Tweeted successfully!')

        if __name__ == '__main__':
            api = api()
            tweet(api, f'''💹NOTICIA💹
            ☎Titulo en ingles: {title}☎''',
            'output.png')

    else:
        print("Nothing")



schedule.every(1).minutes.do(Run)


while True:
    schedule.run_pending()
    time.sleep(1)
