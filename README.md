# Blindy
Simple script for running bruteforce blind MySql injection

The script will run through queries listed in sets in provided file (default-queries.json as default) and try to bruteforce places with `{}` placeholder. If no `{}` placeholder present, the script will simply make request with current query.


## command line
```bash
$ python3 blindy.py --help
usage: blindy.py [-h] [-f filename] [-m method] -p name -r regexp -u url
                 [-s set_of_queries]

Run blind sql injection using brutforce

optional arguments:
  -h, --help            show this help message and exit
  -f filename           File name for your commands in json format, defaults
                        to default-queries.json
  -m method, --method method
                        Where to inject (GET - get parameter/default, POST -
                        post parameter, HEADER - header)
  -p name               Name of parameter (for get - param name, post - param
                        name, for header - name of header). If params need to
                        have fixed value use -p submit=true
  -r regexp             Regular expression for negative pattern (script search
                        for the pattern and if present - will consider that
                        injection failed and igrone result.)
  -u url                Url to test
  -s set_of_queries, --set set_of_queries
                        Which set of queries to analyze from json file, for
                        ex. login, blind. Default to blind.
```

## Example usage

Bruteforce inject into POST `query_param`
```bash
python3 blindy.py -m POST -p query_param -p submit=1 -r 'Pattern\ to\ ignore\ result' -u http://example.com/index.php -s blind
```

Bruteforce inject into POST `query_param` with placeholder
```bash
python3 blindy.py -m POST -p "query_param=login {}" -p submit=1 -r 'Pattern\ to\ ignore\ result' -u http://example.com/index.php -s blind
```
This will inject the queries in a place of `{}` parameter placeholder


Simple check a list of queries against `username` parameter
```bash
python3 blindy.py -m POST -p username -p submit=1 -r 'Pattern\ to\ ignore\ result' -u http://example.com/login.php -s login
```

