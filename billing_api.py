import requests
import constant


class Billingpy:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    @staticmethod
    def billing_login(login, password):
        if len(login) > 10 or len(password) > 10:
            return 'Login or password incorrect'
        else:
            log_str = '%22login%22:%22{}%22,%22passwd%22:%22{}%22'.format(login.upper(), password)
            req = requests.get(constant.bill_url + str(log_str) + '}').json()
            if req.get('user') is not None:
                r = req['user']['abonent']
                subscriber_info = {'name': r['name'], 'tel': r['sms'], 'account': r['__account'][20:],
                                   'tariff': r['__tariff'], 'bill': login}
                return subscriber_info
            elif req.get('error') == 'Неправильный пароль':
                return 'Wrong pass'
            elif req.get('error') == 'Введите логин и пароль.' or req.get('error'.upper()) is not None:
                return 'Input login and pass'
            else:
                return 'Err'


# print(Billingpy.billing_login('test', 'test'))
