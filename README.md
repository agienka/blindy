# Blindy
Simple script for running brute-force blind MySql injection

Note: this script was created for fun, helpful in some ctf challenges :)

## description
* The script will run through queries listed in sets in provided file and try to brute-force any place where `{}` placeholder is found. 
* GET & POST http methods are supported
* Http HEADERS are supported in the same way as other parameters
* In default mode, script looks for negative pattern (text that is not visible when injection succeeds)
* With `--positive` flag one can switch to looking for expected response

## command line interface
```bash
$ python3 blindy.py --help
usage: blindy.py [-h] [-X HTTP_METHOD] -p PARAMETER [-H HTTP_HEADER]
                 [-f FILENAME] -r PATTERN [--positive] [-s QUERY_SET] [-e]
                 [-v]
                 url

Run blind sql injection using brute force

positional arguments:
  url                   Target url

optional arguments:
  -h, --help            show this help message and exit
  -X HTTP_METHOD, --http-method HTTP_METHOD
                        Http method: (GET (default), POST)
  -p PARAMETER, --parameter PARAMETER
                        Parameter, e.g. name=value, name={}
  -H HTTP_HEADER, --http-header HTTP_HEADER
                        Http headers, e.g. X-Custom_header:value,
                        X-Custom_header:{}
  -f FILENAME, --filename FILENAME
                        File with commands in json, default queries.json
  -r PATTERN, --pattern PATTERN
                        Regular expression
  --positive            Injection was successfull if pattern IS PRESENT in
                        response
  -s QUERY_SET, --query-set QUERY_SET
                        Json key for query set, default to ['login']
  -e, --encode          Url encode payload
  -v, --verbose         Print full info what's going on

==================== [example usage] ===================

Bruteforce POST `query_param` parameter:
$ python3 blindy.py http://localhost/index.php -X POST -p query_param={} -p submit=1 -r "Wrong param" -s "['blind']"

Bruteforce POST `query_param` parameter part:
$ python3 blindy.py http://localhost/index.php -X POST -p "query_param=login {}" -p submit=1 -H 'Cookie: PHPSESSID=sdfsdgvdvsdvs' -r "Wrong param" -s "['blind']"

Bruteforce `X-Custom-Header` in GET request - use single query from set:
$ python3 blindy.py http://localhost/index.php -X GET -p admin=1 -H "X-Custom_header: {}" -r "Wrong param" -s "['blind'][0]"

Simple check a list of queries against `username` parameter (negative pattern):
$ python3 blindy.py http://localhost/login.php -X POST -p username={} -p submit=1 -r "Wrong username" -s "['login']"

Simple check a list of queries against `username` parameter (positive pattern):
$ python3 blindy.py http://localhost/login.php -X POST -p username={} -p submit=1 -r "Welcome back, admin" --positive -s "['login']"
```

## running tests
```bash
python3 -m unittest blindy_test.py
```

