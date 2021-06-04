#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser
import json
from jinja2 import Template


class Parserr(HTMLParser):
    payload = list()

    def get_data(self):
        return self.payload

    def handle_data(self, data):
        self.payload.append(str(data))


class S(BaseHTTPRequestHandler):
    def _set_html_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _set_json_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8") 

    def get_stat(self):
        jinja2_template_string = open("table.html", 'rb').read()
        template = Template(jinja2_template_string.decode('utf-8'))
        with open('tasks.json') as outfile:
            data = json.load(outfile)
            page = template.render(output_info=data["tasks"])
            return page.encode("utf8")

    def get_task(self):
        task = ""
        counter = 0
        data = {}
        with open('tasks.json', 'r') as readfile:
            data = json.load(readfile)
            for one_task in data["tasks"]:
                if one_task[1] == "Not completed":
                    task = one_task
                    break
                counter += 1

        if not task == "":
            content = f"<html><body><h1>Task</h1><h2>{task[0]}</h2><h3>{counter}</h3></body></html>"
            task[1] = "In progress"
            with open('tasks.json', 'w') as outfile:
                json.dump(data, outfile)
        else:
            content = f"<html><body><h1>No active tasks</h1></body></html>"
        return content.encode("utf8") 

    def do_GET(self):
        self._set_html_headers()
        req_path = str(self.path)
        payload = ""
        if req_path == "/gettask":
            payload = self.get_task()
        elif req_path == "/table":
            payload = self.get_stat()
        else:
            payload = self._html("Start page")

        self.wfile.write(payload)

    def do_HEAD(self):
        self._set_html_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length)
        payload = post_data.decode()
        info_json = json.loads(payload)
        id = info_json['Task id']
        res = info_json['Task result']
        time = info_json['Time']

        with open('tasks.json', 'r') as outfile:
            data = json.load(outfile)
            tasks = data["tasks"][id]
            tasks[1] = "Completed"
            tasks[2] = str(res)
            tasks[3] = str(time)

        with open('tasks.json', 'w') as outfile:
            json.dump(data, outfile)

        self._set_json_headers()
        result_meaning = {'Result': "OK"}
        json_data = json.dumps(result_meaning)
        self.wfile.write(json_data.encode("utf8"))


def run_server(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print("Server is running")
    httpd.serve_forever()


def reset_tasks():
    with open('unfinished_tasks.json', 'r') as readfile:
        data = json.load(readfile)
        with open('tasks.json', 'w') as outfile:
            json.dump(data, outfile)


if __name__ == "__main__":
    reset_tasks()
    run_server()
