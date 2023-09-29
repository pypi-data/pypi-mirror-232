#!/usr/bin/python

from optparse import OptionParser
import psutil
import pyfiglet


def main():
    def figlet():
        result = pyfiglet.figlet_format('cpu-info')
        print(result)

    parser = OptionParser(add_help_option=False)

    parser.add_option('-h', '--help',
                      action='store_true', dest='help', default=False, help="show this help menu")

    parser.add_option('-c', '--cpu',
                      action='store_true', dest='cpu', default=False, help="shows how many cpu's available")

    parser.add_option('-d', '--disk',
                      action='store_true', dest='disk', default=False, help="disk partitions")

    parser.add_option('-D', '--dpercent',
                      action='store_true', dest='dpercent', default=False, help="disk percentage")

    parser.add_option('-m', '--memusage',
                      action='store_true', dest='memusage', default=False, help="all memory usages")

    parser.add_option('-C', '--cpuload',
                      action='store_true', dest='cpuload', default=False, help="cpu load percentage")

    (option, args) = parser.parse_args()

    try:
        if option.ensure_value('help', False):
            parser.print_help(figlet())

        if option.ensure_value('cpu', False):
            print('number of cpu : ', psutil.cpu_count())

        if option.ensure_value('disk', False):
            print(psutil.disk_partitions())

        if option.ensure_value('dpercent', False):
            print(psutil.disk_usage('/'))

        if option.ensure_value('memusage', False):
            print(psutil.virtual_memory())

        if option.ensure_value('cpuload', False):
            while True:
                print('\rcpu percentage', psutil.cpu_percent(1), '%', end='')
            else:
                print('\rcpu percentage', psutil.cpu_percent(1), '%')

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
