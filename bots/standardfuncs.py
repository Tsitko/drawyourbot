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
    md_parts = {}
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        for content in header.contents:
            if '<' not in str(content) and content is not None:
               md_parts[content] = ''
    # find text
    for header in md_parts.keys():
        target = soup.find('a', id='user-content-' + str(header.lower().replace(' ', '-')))
        md_parts[header] = str(target.find_next('p'))
    # find the best block
    score = 0
    result = ''
    for header in md_parts.keys():
        if md_parts[header] is not None:
            temp_score = 0
            for key_word in query.split(' '):
                for word in md_parts[header].replace('.', '').lower().split(' '):
                    if word == key_word:
                        temp_score += 1
            if temp_score > score:
                score = temp_score
                result = '#' + header.lower().replace(' ', '-')
    return md_path + result
