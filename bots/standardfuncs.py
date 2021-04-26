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
    headers = []
    for header in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        for content in header.contents:
            if '<' not in str(content):
               headers.append(content)
    score = 0
    result = ''
    for header in headers:
        temp_score = 0
        for word in query.split(' '):
            if (word + ' ').lower() in header.lower():
                temp_score += 1
        if temp_score >= score:
            score = temp_score
            result = '#' + header.lower().replace(' ', '-')
    return md_path + result
