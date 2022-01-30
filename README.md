## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This source code will catch URL, title, contents 
from Google search result using BeautifulSoup 
and insert the results into Mongodb. 
Simply use it when you want to put test data into DB.

## Technologies
Project is created with:
* python version: 3.9.1
* Beautiful soap
* Mongodb
	
## Setup
In order to use this source, install these packages.
```
pip install requests
pip install beautifulsoup4
pip install pymongo
pip install lxml
```

## How to run
```
Run debug mode : python ggcrawling.py
Run non-debug mode : python -O ggcrawling.py
```
