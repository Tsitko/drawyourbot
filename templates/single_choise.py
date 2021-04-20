def %block_name%(bot, update):
    global last_question
    options = [%block_options%]
    buttons = []
    for option in options:
        buttons.append([InlineKeyboardButton(option, callback_data=option)])
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.message.reply_text('%block_label%', reply_markup=reply_markup)
    last_question[bot.message.chat_id] = '%block_name%'