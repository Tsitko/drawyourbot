import xml.etree.ElementTree as ET
import base64
import zlib
from urllib.parse import unquote
import re


def make_string(strng):
    strng = strng.replace('"', '\\"')
    strng = strng.replace('\'', "\\'")
    return strng

def make_names(strng):
    strng = re.sub('[^a-zA-Z0-9\n]', '_', strng)
    return strng


def make_label(strng):
    cleanr = re.compile('<.*?>')
    strng = strng.replace('&nbsp;', ' ')
    strng = strng.replace('&quot;', '\"')
    strng= re.sub(cleanr, '', strng)
    return strng


class Arrow(object):
    def __init__(self, element):
        self.id = element.get('id')
        self.source = element.get('source')
        self.target = element.get('target')
        self.label = ''
        self.target_element = None


class Start(object):
    def __init__(self, element):
        self.id = element.get('id')
        self.label = make_label(element.get('value'))
        self.arrow = None


class Message(object):
    def __init__(self, element):
        self.id = element.get('id')
        self.label = element.get('value')
        self.label = make_label(self.label)
        if '[' in self.label and ']' in self.label:
            self.name = self.label.split('[')[1].split(']')[0]
            self.label = self.label.replace('[' + str(self.name) + ']', '')
            self.name = make_names(self.name)
        else:
            self.name = None
        self.arrow = None
        self.type = 'message'


class SingleChoice(object):
    def __init__(self, element):
        self.id = element.get('id')
        self.label = element.get('value')
        self.label = make_label(self.label)
        if '[' in self.label and ']' in self.label:
            self.name = self.label.split('[')[1].split(']')[0]
            self.label = self.label.replace('[' + str(self.name) + ']', '')
            self.name = make_names(self.name)
        else:
            self.name = None
        self.arrows = []
        self.type = 'single choice'


class FunctionsBlock(object):
    def __init__(self, element):
        self.id = element.get('id')
        self.label = element.get('value')
        self.label = make_label(self.label)
        self.library = self.label.split('_functions_')[1].split('::')[0]
        self.function = self.label.split(self.library)[1].split('::')[1]
        self.function = self.function.replace('&quot;', '\"')
        self.function_args = ''
        if '(' in self.function and ')' in self.function:
            self.function_args = self.function.split('(')[1].split(')')[0]
        self.function = self.function.split('(')[0]
        self.arrows = []
        self.type = 'functions block'
        self.name = self.label.split('_functions_')[1].split('(')[0]
        self.name = self.name.replace('::', '_')


class BotStructure(object):
    def __init__(self, path):
        root = ET.parse(path).getroot()
        for type_tag in root.findall('diagram'):
            b = base64.b64decode(type_tag.text)
            result = unquote(zlib.decompress(b, -15).decode('utf8'))
        self.root = ET.fromstring(result)
        self.errors = ''
        self.arrows = []
        self.start = None
        self.messages = []
        self.functions_blocks = []
        self.single_choice_blocks = []
        self.block_names = []

    def get_style(self, element):
        style = element.get('style')
        if style is not None:
            if 'ellipse' in style:
                return 'start point'
            elif 'edgeStyle=orthogonalEdgeStyle' in style:
                return 'arrow'
            elif 'edgeLabel' in style:
                return 'label'
            elif 'rhombus' in style:
                return 'single choice'
            elif 'shape=process' in style:
                return 'functions block'
            else:
                return 'message'
        else:
            return None


    def get_arrows(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'arrow':
                arrow = Arrow(element)
                if arrow.source is None:
                    self.errors += 'One of your arrows start point is not connected to anything\n'
                if arrow.target is None:
                    self.errors += 'One of your arrows end point is not connected to anything\n'
                self.arrows.append(arrow)

    def set_arrow_labels(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'label':
                for i in range(len(self.arrows)):
                    if element.get('parent') == self.arrows[i].id:
                        self.arrows[i].label = element.get('value')

    def load_arrows(self):
        self.arrows = []
        self.get_arrows()
        self.set_arrow_labels()

    def get_start_point(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'start point':
                self.start = Start(element)
        if self.start.label is None:
            self.errors += 'Your diagram should have start point with your bots token'

    def get_start_arrow(self):
        for arrow in self.arrows:
            if arrow.source == self.start.id:
                self.start.arrow = arrow
        if self.start.arrow is None:
            self.errors += 'No arrows are connected to your start point\n'

    def load_start_point(self):
        self.get_start_point()
        self.get_start_arrow()

    def get_messages(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'message':
                msg = Message(element)
                self.messages.append(msg)
                if msg.name is not None:
                    self.block_names.append(msg.name)

    def get_messages_arrows(self):
        for j in range(len(self.arrows)):
            for i in range(len(self.messages)):
                if self.arrows[j].source == self.messages[i].id:
                    self.messages[i].arrow = self.arrows[j]
                if self.arrows[j].target == self.messages[i].id:
                    self.arrows[j].target_element = self.messages[i]

    def load_messages(self):
        self.get_messages()
        self.get_messages_arrows()

    def get_single_choices(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'single choice':
                single_choise_block = SingleChoice(element)
                if single_choise_block.name is None:
                    self.errors += 'One of your single choice blocks have no name\n'
                else:
                    self.block_names.append(single_choise_block.name)
                self.single_choice_blocks.append(single_choise_block)

    def get_single_choices_arrows(self):
        for j in range(len(self.arrows)):
            for i in range(len(self.single_choice_blocks)):
                if self.arrows[j].source == self.single_choice_blocks[i].id:
                    self.single_choice_blocks[i].arrows.append(self.arrows[j])
                    if self.arrows[j].label is None:
                        self.errors += 'Some of arrow for your ' + str(self.single_choice_blocks[i].name) + ' block arrows have no label\n'
                if self.arrows[j].target == self.single_choice_blocks[i].id:
                    self.arrows[j].target_element = self.single_choice_blocks[i]
        for i in range(len(self.single_choice_blocks)):
            if len(self.single_choice_blocks[i].arrows) == 0:
                self.errors += 'Your single choice block ' + str(self.single_choice_blocks[i].name) + ' have no arrows\n'

    def load_single_choices(self):
        self.get_single_choices()
        self.get_single_choices_arrows()

    def get_functions_blocks(self):
        for element in self.root.iter('mxCell'):
            if self.get_style(element) == 'functions block':
                self.functions_blocks.append(FunctionsBlock(element))

    def get_functions_blocks_arrows(self):
        for j in range(len(self.arrows)):
            for i in range(len(self.functions_blocks)):
                if self.arrows[j].source == self.functions_blocks[i].id:
                    self.functions_blocks[i].arrows.append(self.arrows[j])
                    if self.arrows[j].label != 'True' and self.arrows[j].label != 'False':
                        self.errors += 'You can use only False and True labeled arrows for you functions block\n'
                if self.arrows[j].target == self.functions_blocks[i].id:
                    self.arrows[j].target_element = self.functions_blocks[i]
        for i in range(len(self.functions_blocks)):
            if len(self.functions_blocks[i].arrows) == 0:
                self.errors += 'One of your functions blocks have no arrows\n'

    def load_functions_blocks(self):
        self.get_functions_blocks()
        self.get_functions_blocks_arrows()

    def get_element_by_name(self, name):
        for element in self.messages:
            if element.name == name:
                return element
        for element in self.single_choice_blocks:
            if element.name == name:
                return element

    def load_all(self):
        self.load_arrows()
        self.load_start_point()
        self.load_messages()
        self.load_single_choices()
        self.load_functions_blocks()

