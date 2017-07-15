import argparse

class CliOptions:

    def red(self, prt):
        return "\033[91m{}\033[00m".format(prt)

    def green(self, prt):
        return "\033[92m{}\033[00m".format(prt)

    def yellow(self, prt):
        return "\033[93m{}\033[00m".format(prt)

    def magenta(self, prt):
        return "\033[95m{}\033[00m".format(prt)

    def cyan(self, prt):
        return "\033[96m{}\033[00m".format(prt)

    def grey(self, prt):
        return "\033[37m{}\033[00m".format(prt)

    def status(self, code):
        if code < 300:
            return self.green(code)
        if code < 400:
            return self.yellow(code)
        if code < 500:
            return self.magenta(code)
        if code < 600:
            return self.red(code)
        else:
            return code

    def parseArguments(self):
        parser = argparse.ArgumentParser(description="Run blind sql injection using brute force",
                                         formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
==================== [example usage] ===================
         
Bruteforce POST `query_param` parameter:
$ python3 blindy.py -X POST -p query_param={} -p submit=1 -r "negative pattern" -u http://example.com/index.php -s blind

Bruteforce POST `query_param` parameter part:
$ python3 blindy.py -X POST -p "query_param=login {}" -p submit=1 -r "negative pattern" -u http://example.com/index.php -s blind

Bruteforce `X-Custom-Header` in POST request:
$ python3 blindy.py -X POST -p someparam=param -H "X-Custom_header: {}" -r "negative pattern" -u http://example.com/index.php -s blind

Simple check a list of queries against `username` parameter (negative pattern):
$ python3 blindy.py -X POST -p username={} -p submit=1 -r "Hi stranger, please sign in!" -u http://example.com/login.php -s login

Simple check a list of queries against `username` parameter (positive pattern):
$ python3 blindy.py -X POST -p username={} -p submit=1 -r "Welcome back, Admin!" --positive -u http://example.com/login.php -s login
        ''')
        parser.add_argument('-f', '--filename', default='default-queries.json',
                            type=argparse.FileType('r'),
                            help='File name for your commands (json), default default-queries.json')
        parser.add_argument('-u', '--url', required=True, help='')
        parser.add_argument('-X', '--http-method',
                            help='Http method: (GET (default), POST)', default='GET')
        parser.add_argument('-p', '--parameter', required=True, action='append',
                            help='Parameter, e.g. name=value, name={}')
        parser.add_argument('-H', '--http-header', action='append',
                            help='Http headers, e.g. X-Custom_header:value, X-Custom_header:{}')
        parser.add_argument('-r', '--pattern', required=True,
                            help='Regular expression/pattern')
        parser.add_argument('--positive', action='store_const', const=True,
                            help='Injection was successfull if pattern IS PRESENT in response')
        parser.add_argument('-s', '--query-set', default='blind',
                            help='Set of queries from loaded file, e.g. login, blind. Default to blind.')
        parser.add_argument('-e', '--encode', metavar='encode', action='store_const', const=True, help='Url encode payload')
        parser.add_argument('-v', '--verbose', action='store_const', const=True, help='Print full info what\'s going on')
        args = parser.parse_args()

        return args