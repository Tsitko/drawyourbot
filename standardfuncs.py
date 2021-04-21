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
