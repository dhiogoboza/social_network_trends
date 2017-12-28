# social network trends

## Description

Tool to show trending topics in places based o Twitter API. This project is result of a UFRN class work from Tópicos Especiais em Processamento da Informação.

## Run

### Requirements

* [Google AppEngine Python Development Environment](https://cloud.google.com/python/setup)
* [Google Cloud SDK](https://cloud.google.com/appengine/docs/standard/python/download)

Once you have installed all requirements successfully, type the following from
repository root:

```
dev_appserver.py app.yaml
```

`social network trends` normally will be running on localhost:8080. If anything
goes wrong, send us an issue.

### Deploy

To deploy to Google AppEngine you should first [create a new GCP project and
AppEngine application](https://console.cloud.google.com/projectselector/appengine/create?lang=python&st=true&_ga=2.72010202.832757452.1514418811-644892018.1504660114). Then do the following:

```
gcloud app deploy
```

## Screenshots

![Screenshot 01](/screenshots/screenshot01.png?raw=true "Relevance of 'World' at world")
![Screenshot 02](/screenshots/screenshot02.png?raw=true "Trending topics at Brazil")

## Contributors

* Dhiogo Boza <dhiogoboza@gmail.com>
* Evandro Carlos <evandro.carlos92@gmail.com>
* Ruben Oliveira Chiavone <rubenochiavone@gmail.com>

## Available at

[https://tepi-global-trends.appspot.com/](https://tepi-global-trends.appspot.com/)
