# Q-DashMan
Generating dashboard the simple way using GrimoireLab tools in a Django app.

# Installation
`$ git clone https://github.com/zhquan/Q-DashMan.git`

`$ cd Q-DashMan`

`$ python3 manage.py runserver`

`$ python3  manage.py migrate`

`$ python3 manage.py makemigrations`

# Docker containers
You need a ElasticSearch, Kibana, and MariaDB running in a docker container.

### ElasticSearch
docker-compose.yml
```
elasticsearch:
  restart: on-failure:5
  image: elasticsearch:5.1.1
  command: elasticsearch -Enetwork.bind_host=0.0.0.0 -Ehttp.max_content_length=2000mb
  environment:
    - ES_JAVA_OPTS=-Xms2g -Xmx2g
  expose:
    - "9200"
  ports:
    - "9200:9200"
  log_driver: "json-file"
  log_opt:
    max-size: "100m"
    max-file: "3"
```

### Kibana
docker-compose.yml
```
kibana:
  restart: on-failure:5
  image: kibana:5.1.1
  environment:
    - NODE_OPTIONS=--max-old-space-size=1000
  links:
    - elasticsearch
  ports:
    - "5601:5601"
  log_driver: "json-file"
  log_opt:
      max-size: "100m"
      max-file: "3"
```

### MariaDB
docker-compose.yml
```
mariadb:
  restart: on-failure:5
  image: mariadb:10.0
  expose:
    - "3306"
  environment:
    - MYSQL_ROOT_PASSWORD=
    - MYSQL_ALLOW_EMPTY_PASSWORD=yes
  command: --wait_timeout=2592000 --interactive_timeout=2592000 --max_connections=300
  log_driver: "json-file"
  log_opt:
      max-size: "10
```

### Mordred
Remember the path of this docker-compose.yml
<mordred_conf_path>: The same path as docker-compose.yml
<mordred_logs_path>: <mordred_conf_path>/logs

docker-compose.yml
```
redis:
  image: redis

mordred:
  restart: on-failure:5
  image: bitergia/mordred:18.05-03
  volumes:
    - <mordred_conf_path>:/home/bitergia/conf
    - <mordred_logs_path>:/home/bitergia/logs
  links:
    - redis
  external_links:
    - elasticsearch_elasticsearch_1:elasticsearch
    - mariadb_mariadb_1:mariadb

  log_driver: "json-file"
  log_opt:
      max-size: "100m"
      max-file: "3"
```

# Modify `models.py`
When you modify the `module.py` file, you have to delete the old database and create a new one.
`$ python3 rm db.sqlite3`

`$ python3 manage.py migrate`

`$ python3 manage.py makemigrations`

`$ python3 manage.py createsuperuser`

# License
Licensed under GNU General Public License (GPL), version 3 or later.
