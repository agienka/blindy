# Blindy
Simple script for running brute-force blind MySql injection

Note: this script was created for fun, helpful in some ctf challenges :)

## description
* The script will run through queries listed in sets in provided file and try to brute-force any place where `{}` placeholder is found. 
* GET & POST http methods are supported
* Http HEADERS are supported in the same way as other parameters
* In default mode, script looks for negative pattern (text that is not visible when injection succeeds)
* With `--positive` flag one can switch to looking for known response

## command line interface
```bash
$ python3 blindy.py --help
usage: blindy.py [-h] [-f FILENAME] -u URL [-X HTTP_METHOD] -p PARAMETER
                 [-H HTTP_HEADER] -r PATTERN [--positive] [-s QUERY_SET] [-e]
                 [-v]

Run blind sql injection using brute force

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        File name for your commands (json), default default-
                        queries.json
  -u URL, --url URL
  -X HTTP_METHOD, --http-method HTTP_METHOD
                        Http method: (GET (default), POST)
  -p PARAMETER, --parameter PARAMETER
                        Parameter, e.g. name=value, name={}
  -H HTTP_HEADER, --http-header HTTP_HEADER
                        Http headers, e.g. X-Custom_header:value,
                        X-Custom_header:{}
  -r PATTERN, --pattern PATTERN
                        Regular expression/pattern
  --positive            Injection was successfull if pattern IS PRESENT in
                        response
  -s QUERY_SET, --query-set QUERY_SET
                        Set of queries from loaded file, e.g. login, blind.
                        Default to blind.
  -e, --encode          Url encode payload
  -v, --verbose         Print full info what's going on

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
```

## running tests
```bash
python3 -m unittest blindy_test.py
```

