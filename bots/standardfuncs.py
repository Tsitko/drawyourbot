import requests
from bs4 import BeautifulSoup

def contains(data, *args):
    result = False
    for arg in args:
        if arg in data or arg.lower() in data.lower():
            result = True
    return result


def save_answers(data, *args):
    message = ''
    log_name = args[0]
    for key in data.keys():
        message += str(key) + ': ' + str(data[key]) + '\n'
    try:
        with open(log_name, 'a') as file:
            file.write(message + '\n\n')
        return True
    except:
        return False


def search_md(*args):
    query = args[0].replace('?', '')
    md_path = args[1]
    md = requests.get(md_path).content.decode()
    soup = BeautifulSoup(md, 'html.parser')
    # get readme content
    soup = soup.find_all('readme-toc')[0]
    # get headers
    headers = []
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        for content in header.contents:
            if '<' not in str(content):
               headers.append(content)
    # find text
    texts = []
    for h1 in headers:
        target = soup.find('a', id='user-content-' + str(h1.lower().replace(' ', '-')))
        texts.append(str(target.find_next('p')))
    # find the best block
    score = 0
    result = ''
    if len(texts) == len(headers):
        for i in range(len(headers)):
            if texts[i] is not None and headers[i] is not None:
                temp_score = 0
                for word in query.split(' '):
                    if str(word + ' ').lower() in texts[i].lower():
                        temp_score += 1
                if temp_score > score:
                    score = temp_score
                    result = '#' + headers[i].lower().replace(' ', '-')
    return md_path + result
