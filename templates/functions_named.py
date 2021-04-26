def %block_name%(bot, update):
    global answers
    answers[bot.message.chat_id]["%block_special_name%"] = %function%(%function_args%)
