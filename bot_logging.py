from pymongo import MongoClient


class BotTLog:
    @staticmethod
    def log_user(message):
        if log.find_one({'chat_id': message.chat.id}) is None:
            log.insert({'chat_id': message.chat.id,
                        'info': {'id': message.from_user.id,
                                 'first': message.from_user.first_name,
                                 'last': message.from_user.last_name,
                                 'lang': message.from_user.language_code},
                        'messages': {str(message.message_id): {
                            'text': message.text,
                            'date': message.date,
                            'content_type': message.content_type}}})
        else:
            log.update_one({'chat_id': message.chat.id}, {'$set': {'messages.%s' % message.message_id:
                                                                        {'is_bot': False,
                                                                         'text': message.text,
                                                                         'date': message.date,
                                                                         'content_type': message.content_type}}})

    @staticmethod
    def log_bot(answer):
        if answer is None:
            pass
        else:
            message_id = answer['message_id']
            log.update_one({'chat_id': answer['chat'].__dict__['id']}, {'$set': {'messages.%s' % message_id:
                                                                        {'is_bot': True,
                                                                         'text': answer['text'],
                                                                         'date': answer['date'],
                                                                         }}})


mongo = MongoClient()

log = mongo.bot_t.log
