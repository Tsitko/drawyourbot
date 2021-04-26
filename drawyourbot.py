from BotStructure import *
import sys


class BotCode(object):
    def __init__(self, BS, token):
        self.BS = BS
        self.imports = ''
        self.single_choice_functions = ''
        with open('templates/bot_template.py', 'r') as file:
            self.code = file.read()
        self.token = token

    def set_imports(self):
        code_part = ''
        for func in self.BS.functions_blocks:
            code_part += 'from ' + str(func.library) + ' import ' + str(func.function.split('(')[0]) + '\n'
        self.code = self.code.replace('%import_functions%', code_part)

    def set_token(self):
        self.code = self.code.replace('%token%', self.token)

    def set_single_choice_functions(self):
        code_part = ''
        with open('templates/single_choise.py', 'r') as file:
            template = file.read()
        for single_choice in self.BS.single_choice_blocks:
            tmp = template
            tmp = tmp.replace('%block_name%', str(single_choice.name))
            tmp = tmp.replace('%block_label%', str(single_choice.label))
            options = ''
            for arrow in single_choice.arrows:
                options += '\"' + str(arrow.label) + '\", '
            options = options[:-2]
            tmp = tmp.replace('%block_options%', options)
            code_part += tmp + '\n\n'
        self.code = self.code.replace('%single_choice_functions%', code_part)

    def make_message(self, message, indent, inline=False):
        code_part = ''
        label = make_string(message.label)
        for name in self.BS.block_names:
            if not inline:
                if '__' + str(name) + '__' in label:
                    label = label.replace('__' + str(name) + '__', '\" + str(answers[bot.message.chat_id]'
                                                                   '[\"' + str(name) + '\"]) + \"')
            else:
                if '__' + str(name) + '__' in label:
                    label = label.replace('__' + str(name) + '__', '\" + str(answers[query.message.chat_id]'
                                                                   '[\"' + str(name) + '\"]) + \"')
        if message.name is None:
            if not inline:
                with open('templates/message.py', 'r') as file:
                    code_part += indent
                    code_part += file.read()
                code_part = code_part.replace('%message_text%', label)
            else:
                with open('templates/message_inline.py', 'r') as file:
                    code_part += indent
                    code_part += file.read()
                code_part = code_part.replace('%message_text%', label)
        else:
            if not inline:
                with open('templates/message_with_name.py', 'r') as file:
                    tmp = file.read()
                for line in tmp.split('\n'):
                    code_part += indent + line + '\n'
                code_part = code_part[:-1]
                code_part = code_part.replace('%message_text%', label)
            else:
                with open('templates/message_with_name_inline.py', 'r') as file:
                    tmp = file.read()
                for line in tmp.split('\n'):
                    code_part += indent + line + '\n'
                code_part = code_part[:-1]
                code_part = code_part.replace('%message_text%', label)
            code_part = code_part.replace('%block_name%', message.name)
        return code_part


    def get_chain(self, arrow):
        chain = [arrow.target_element]
        if chain[-1].type == 'message':
            if chain[-1].arrow is not None:
                while chain[-1].name is None and chain[-1].arrow is not None:
                    chain.append(chain[-1].arrow.target_element)
        return chain

    def build_chain(self, chain, indent, inline=False):
        code_part = ''
        for element in chain:
            if inline:
                if element.type == 'message':
                    code_part += self.make_message(element, indent, inline=True) +'\n'
                else:
                    code_part += indent + str(element.name) + '(query, update)' + '\n'
            else:
                if element.type == 'message':
                    code_part += self.make_message(element, indent, inline=False) +'\n'
                else:
                    code_part += indent + str(element.name) + '(bot, update)' + '\n'
        return code_part

    def build_functions_chain(self, element):
        code_part_true = ''
        code_part_false = ''
        if element.type == 'functions block':
            for arrow in element.arrows:
                if arrow.label == 'True':
                    code_part_true = self.build_chain(self.get_chain(arrow), indent='        ', inline=False)
                elif arrow.label == 'False':
                    code_part_false = self.build_chain(self.get_chain(arrow), indent='        ', inline=False)
        return code_part_true, code_part_false

    def set_functions_block_functions(self):
        code_part = ''
        names = []
        for element in self.BS.messages:
            if element.name is not None:
                names.append(element.name)
        for element in self.BS.functions_blocks:
            if len(element.arrows) == 2:
                with open('templates/functions.py', 'r') as file:
                    template = file.read()
            if len(element.arrows) == 1:
                with open('templates/functions_named.py', 'r') as file:
                    template = file.read()
            next_blocks_true, next_blocks_false = self.build_functions_chain(element)
            template = template.replace('%block_name%', element.name)
            if element.special_name is not None:
                template = template.replace('%block_special_name%', element.special_name)
            template = template.replace('%function%', element.function)
            if len(element.function_args) > 0:
                if ',' in element.function_args:
                    if str(element.function_args.split(',')[0]) in names:
                        name = str(element.function_args.split(',')[0])
                        element.function_args = element.function_args.replace(name, 'answers[bot.message.chat_id]'
                                                                                    '[\"' + str(name) + '\"]')
                    element.function_args = element.function_args.replace('answers,', 'answers[bot.message.chat_id],')
                else:
                    if str(element.function_args) in names:
                        name = str(element.function_args)
                        element.function_args = element.function_args.replace(name, 'answers[bot.message.chat_id]'
                                                                                    '[\"' + str(name) + '\"]')
                    element.function_args = element.function_args.replace('answers', 'answers[bot.message.chat_id]')
            template = template.replace('%function_args%', element.function_args)
            template = template.replace('%next_blocks_true%', next_blocks_true)
            template = template.replace('%next_blocks_false%', next_blocks_false)
            if len(element.arrows) == 1:
                code_part += template + str(self.build_chain(self.get_chain(element.arrows[0]), indent='    ', inline=False)) + '\n'
            else:
                code_part += template + '\n'
        self.code = self.code.replace('%functions_blocks_functions%', code_part)

    def set_first_blocks(self):
        first_blocks = self.build_chain(self.get_chain(self.BS.start.arrow), indent='    ', inline=False)
        self.code = self.code.replace('%first_blocks%', first_blocks)

    def set_inline_handlers(self):
        code_part = ''
        for element in self.BS.single_choice_blocks:
            template = '    if last_question[query.message.chat_id] == \'' + str(element.name) + '\':\n'
            for arrow in element.arrows:
                with open('templates/options_handler.py', 'r') as file:
                    template += file.read()
                template = template.replace('%option%', make_string(arrow.label))
                template = template.replace('%next_blocks%', self.build_chain(self.get_chain(arrow),
                                                                              indent='             ', inline=True))
            code_part += template + '\n'
        self.code = self.code.replace('%inline_handlers%', code_part)

    def set_text_handlers(self):
        code_part = ''
        for element in self.BS.messages:
            if element.name is not None and element.arrow is not None:
                with open('templates/text_handlers.py') as file:
                    template = file.read()
                template = template.replace('%block_name%', element.name)
                template = template.replace('%get_answer%', '        answers[bot.message.chat_id]'
                                                            '[last_question[bot.message.chat_id]] = bot.message.text')
                template = template.replace('%next_blocks%', self.build_chain(self.get_chain(element.arrow),
                                                                              indent='        ', inline=False))
                code_part += template
        self.code = self.code.replace('%text_handlers%', code_part)

    def make_bot(self):
        self.set_imports()
        self.set_token()
        self.set_single_choice_functions()
        self.set_functions_block_functions()
        self.set_first_blocks()
        self.set_inline_handlers()
        self.set_text_handlers()

    def write_code(self, bot_name):
        self.make_bot()
        with open('bots/' + str(bot_name) + '.py', 'w') as file:
            file.write(self.code)

draw = None
BS = None

try:
    draw = sys.argv[1]
except:
    pass


if draw is None:
    print('You need to add a path to your draw.io file')
else:
    BS = BotStructure(draw)
    BS.load_all()

if BS is not None:
    if BS.errors == '':
        BC = BotCode(BS, BS.start.label)
        bot_name = draw.split('.')[0]
        if '/' in bot_name:
            bot_name = bot_name.split('/')[1]
        if '\\' in bot_name:
            bot_name = bot_name.split('\\')[1]
        BC.write_code(bot_name)
    else:
        print(BS.errors)
