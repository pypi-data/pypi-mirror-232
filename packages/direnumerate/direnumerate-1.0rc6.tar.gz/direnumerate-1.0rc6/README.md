# Direnumerate

## Description

Direnumerate is an open source tool written in Python designed to automate directory and file enumeration on web servers. It is useful for security professionals and system administrators who want to identify hidden resources and assess the security of web applications.

## Key Features

- Enumeration of directories and files on web servers.
- Wordlist customization.
- Detailed output of findings.
- Support for multiple URL schemes (http, https, etc.).

## pip:

    pip install direnumerate

-----------------

## usage:

```python

from direnumerate import DirScan

url = "http://www.exemplo.com"
wordlist = "wordlist.txt"

enum = DirScan(url, wordlist)
enum.dir_enum()
```

----------

## Command line:

    direnumerate -u http://www.exemple.com -w wordlist.txt

## Exemple:

![Captura de tela de 2023-09-26 22-12-27](https://github.com/JuanBindez/direnumerate/assets/79322362/8bf19f41-5225-40cc-a1d8-6dd25a601d4c)

