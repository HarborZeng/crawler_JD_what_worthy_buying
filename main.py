import sys
import getopt

headers = {'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/66.0.3359.117 Safari/537.36"}


def get_url_from_command_args(argv):
    try:
        opts, args = getopt.getopt(argv, "u:", [])
    except getopt.GetoptError:
        print('usage: main.py -url url')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -url url')
            sys.exit()
        elif opt == '-u':
            url = arg
            return url


def main(argv):
    args = get_url_from_command_args(argv)
    print(args)


if __name__ == '__main__':
    main(sys.argv[1:])
