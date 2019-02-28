import librouteros
from time import sleep
import constant


class RouterInfo:
    @staticmethod
    def ping(bill):
        api_m = librouteros.connect(username=constant.login_01, host=constant.ip_01, password=constant.password_25)

        leases_all = api_m(cmd='/ip/dhcp-server/lease/print')

        for lease in leases_all:
            if lease.get('server') == 'AbonNet2' and lease.get('host-name') == bill:
                host = lease['active-address']

                try:
                    r_api = librouteros.connect(host=host, username=constant.login_02, password=constant.password_25)
                except librouteros.exceptions.TrapError:
                    return 'Router is not accessible.'
                ping_office = r_api(cmd='/ping', address=constant.ip_02, count=1)[0]
                ping_google = r_api(cmd='/ping', address='8.8.8.8', count=1)[0]

                if ping_google['packet-loss'] == 0:
                    ping_list = 'average ping to our office : ' + ping_office['avg-rtt'] + '\n' + \
                                'average ping to google.com : ' + ping_google['min-rtt']
                else:
                    ping_list = 'average ping to out office : ' + ping_office['avg-rtt'] + '\n' + \
                                'average ping to google.com : Timeout'
                    pass
                return ping_list
            else:
                pass

        return 'No router found.'

    @staticmethod
    def speed(bill):
        api_m = librouteros.connect(username=constant.login_01, host=constant.ip_01, password=constant.password_08)

        leases_all = api_m(cmd='/ip/dhcp-server/lease/print')

        for lease in leases_all:
            if lease.get('server') == 'AbonNet2' and lease.get('host-name') == bill:
                host = lease['active-address']

                r_api = librouteros.connect(host=host, username=constant.login_02, password=constant.password_25)
                speed = r_api(cmd='/tool/bandwidth-test', address=constant.sp_ip, protocol='tcp', duration=5)
                result = 'Your speed is:' + str(format(speed[-1]['rx-total-average'] / 1000000, '.1f')) + 'Mbps'

                return result

    @staticmethod
    def monitor_pppoe(host):
        api = librouteros.connect(host=host, password=constant.password_25, username=constant.login_02)
        for i in range(10):
            mon = api(cmd='/interface/monitor-traffic', interface='pppoe-out1', once='yes')[-1]
            rx = mon['rx-bits-per-second']
            tx = mon['tx-bits-per-second']
            if rx < 10000 and tx < 10000:
                pass
            else:
                return False
            sleep(1)
        return True
