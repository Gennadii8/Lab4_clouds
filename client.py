#!/usr/bin/env python3

import http.client
from html.parser import HTMLParser
import sympy
import json
import time


class Parserr(HTMLParser):

    payload = list()

    def get_data(self):
        return self.payload

    def handle_data(self, data):
        print("Encountered some data :", data)
        self.payload.append(str(data))


connection = http.client.HTTPConnection('localhost', 8000)
connection.request("GET", "/gettask")
response = connection.getresponse()
print("Status: {} and reason: {}".format(response.status, response.reason))
headers = response.getheaders()
print(headers)

data = response.read().decode()
parser = Parserr()
parser.feed(data)
payload = parser.get_data()
print(payload)

status = payload[0]

if status == "Task":
    task = payload[1].split(" ")
    id = int(payload[2])
    type = task[0]
    number = int(task[1])
    power = int(task[2])
    t1 = time.time()
    res = False
    if type == "IsPrime":
        res = sympy.isprime(number**power - 1)
    t2 = time.time()
    timeInMs = round(t2 - t1, 10)
    print(type + " " + str(res))
    print("Time: " + str(timeInMs))

    foo = {'Task id': id, 'Task result': res, 'Time': timeInMs}
    json_data = json.dumps(foo)

    headers = {'Content-type': 'application/json', 'Content-Length': len(json_data)}

    connection.request('POST', '/post', json_data, headers)

    response = connection.getresponse()
    respstat = response.read().decode()
    print(respstat)

connection.close()
