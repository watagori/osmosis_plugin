# osmosis plugin
## docker
### for start
$ docker-compose up -d

### for access to shell in the container
$ docker-compose exec osmosis_plugin bash

### for end
$ docker-compose down

### for remove
$ docker-compose down --rmi all --volumes --remove-orphans

### For test

```
$ pip install -e .[test]
$ pytest --cov=src --cov-branch --cov-report=term-missing -vv
```
