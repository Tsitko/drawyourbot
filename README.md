# README ![start point](images/drawyourbot_small.png)  

![project demo](project_demo.gif)

Contents:  

- [Draw your bot](#draw-your-bot)  
    - [Install requirements](#install-requirements)
    - [Registering a telegram bot](#registering-a-telegram-bot)
    - [Draw bot](#drawing-a-bot)
        - [Start point](#start-point)
        - [Message block](#message-block)
        - [Single choice block](#single-choice-block)
        - [Functions block](#functions-block)
    - [Generating bot code](#generating-bot-code)  
- [Custom classes](#custom-classes)
    - [Arrow](#arrow)
    - [Start](#start)
    - [Message](#message)
    - [SingleChoice](#singlechoice)
    - [FunctionsBlock](#functionsblock)
    - [BotStructure](#botstructure)
    - [BotCode](#botcode)
- [Standard functions](#standard-functions)
    - [contains](#contains)
    - [save_answers](#save_answers)
- [Examples](#examples)

# Draw your bot
Draw your bot is an open sourced project made to let people construct chat bots without coding or with minimal coding.
You can just draw your chat bot logic in draw.io and generate its code.  
This project will be most useful for those who need to make simple support or survey bot.  
It could also save some time for those who are building really complex bots. In that cases generated bot can be
just a start point.

## Install requirements
First you need to install requirements from requirements.txt.  
The only requirement is python-telegram-bot library.  
To install the requirements just use the following command:  
```
python -m pip install -r requirements.txt --user
```
## Registering a telegram bot
Now you need to register your bot in telegram and get its token. You can register your bot using /newbot command in
[botfather](https://t.me/botfather) telegram bot.  
[Here are the instructions](https://core.telegram.org/bots#6-botfather)

## Drawing a bot
As you registered your bot and got its token, you need to draw your bot logic in [draw.io](https://draw.io/).  
### Start point
Your bot should have exactly one start point. That is a circle or ellipse with your bot token as label:  
![start point](images/start_point.png)  
Your start point should have exactly one arrow.
### Message block
There are two types of messages: with name (that message will wait for users answer and you will be able to use that 
answer in your [functions blocks](#functions-block) and without name (that is just a text message which bot will print out).
Both are drawing as rectangle and should not have more when one outgoing arrow. Name of the message should be in
 square brackets at the beginning of blocks label.
Message with name example:  
![message with name](images/message_with_name.png)  

Message without name example:  
![message with name](images/message.png)  
### Single choice block
For single choice block you should use rhombus. It should always have name and each outgoing line should have label
which will be options in your bot.  
On your draw it will looks like that:  
![single choice](images/single_choice.png)  
  
And in your bot like that:  
![single choice in bot](images/single_choice_in_bot.png)    
### Functions block
You can use functions in your bot. There are some useful functions in standardfuncs.py and you can make your own file
with functions.  
All functions should have exactly two outcomes: True and False.  
You can use answers to your named message blocks and single choice blocks by providing blocks name to functions and
you can use all answers by providing *answers* keyword to your functions. And you can also use any other hardcoded 
parameters (for strings you should use quotes).  
Function should start with \_functions\_ keyword and contain the name of python file with your functions (without 
extension) and function name with its parameters.  
Example: \_functions\_fileWithFunctions::function(argument1, argument2, "string1", "string2")  
In your draw it will looks like that:  
![functions block](images/functions_block.png)    
## Generating bot code
To generate your bot code use the following command:  
```
python drawyourbot.py path_to_your_drawio_file
```
Your bot will be saved to **bots** path. To run it use the following command:  
```
python path_to_your_bot_file
```

# Custom classes
## Arrow
Arrow is a class for arrows.  
It have the following attributes:  
- id: string (arrow id)
- source: string (source element id)
- target: string (target element id)
- label: string (arrow label)
- target_element: Message, SingleChoice or FunctionsBlock (the target element for the arrow)
## Start
Start is a class for start point.  
It have the following attributes:
- id: string (start element id)
- label: string (start element label, which should be your telegram bot token)
- arrow: Arrow (start points outgoing arrow)
## Message
Message is a class for message blocks.  
It have the following attributes:
- id: string (message block id)
- label: string (message text)
- name: string (message block name)
- arrow: Arrow (message block outgoing arrow)
- type: string (always "message")
## SingleChoice
SingleChoice is a class for single choice blocks.  
It have the following attributes:
- id: string (single choice block id)
- label: string (single choice text)
- name: string (single choice block name)
- arrows: list of Arrow (single choice block outgoing arrows)
- type: string (always "single choice")
## FunctionsBlock
FunctionsBlock is a class for functions blocks.  
It have the following attributes:
- id: string (functions block id)
- library: string (file with function)
- function: string (function with arguments)
- name: string (function name)
- function_args: string (function arguments in one string)
- arrows: list of arrow (functions block outgoing arrows)
- type: string (always "functions block")
## BotStructure
BotStructure class is initializing with the path to drawio file and loads its structure.  
It have the following attributes:
- root: xml.etree.ElementTree (xml with bot structure)
- errors: string (errors in bot structure drawio)
- arrows: list of Arrow (arrows from drawio)
- start: Start (start point)
- messages: list of Message (message blocks)
- functions_blocks: list of FunctionsBlock (function blocks)
- single_choice_blocks: list of SingleChoice (single choice blocks)
## BotCode 
BotCode class initializing with BotStructure object. It generates bot code (*make_bot()* function) and writes that code
into file (*write_code()* function).
# Standard functions
## contains
Checks if first argument contains all of other arguments.  
All arguments should be strings (it could be the names of message and single choice blocks - in that case function will
check users answers to those blocks).
## save_answers
Saves all users answers into file.  
Takes *answers* keyword and the name of the file where it should save answers. 
# Examples
To generate a bot from drawio file in **examples** folder you need to open it in draw.io and change "bot_token" on start point to your
[bots token](#registering-a-telegram-bot).  
After that just use the following command:  
```
python drawyourbot.py examples/drawio_file_name.drawio
```
Your bot will be saved into **bots**. You can run it with the following command:  
```
python bots/drawio_file_name.py
```