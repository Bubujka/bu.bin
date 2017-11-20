#!/usr/bin/env python3
import sys

from bs4 import BeautifulSoup
soup = BeautifulSoup(sys.stdin.read())
print(soup.prettify())
