# osmosis plugin

## docker

### For start

$ docker-compose up -d

### For access to shell in the container

$ docker-compose exec osmosis_plugin bash

### For end

$ docker-compose down

### For remove

$ docker-compose down --rmi all --volumes --remove-orphans

### For test

in the container

```
$ cd /app
$ pip install -e .[test]
$ pytest --cov=src --cov-branch --cov-report=term-missing -vv
```

### For execution

in the container

```
$ cd /app
$ pip install -e .[main]
$ python src/main.py address > result.csv
e.x. $ python src/main.py osmo1f2rznaz9s6cwevtfwyq8daguajqaac0yahsgqm > result.csv
```
