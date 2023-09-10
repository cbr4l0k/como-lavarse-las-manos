import shutil

from Report import Report
import sys
import os
from dotenv import load_dotenv
import http.server
import socketserver


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="../front", **kwargs)


load_dotenv()


def main():
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

    # check if tree is installed
    if not shutil.which("tree"):
        print(RED + "Please install tree" + END)
        return

    if len(sys.argv) < 2:
        print(RED + "Usage: python3 snoo.py <project_name>" + END)
        return

    project_name = sys.argv[1]
    print(BLUE + "Generating report for project", project_name + END)

    report = Report(project_name)
    report.complete_report()
    PORT = 8004

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(BLUE + "serving at port" + END, PORT)
            httpd.serve_forever()
        # start google chrome
        os.system(f"google-chrome http://localhost:{PORT}")
    except KeyboardInterrupt:
        print(BLUE + "Stopping the server..." + END)
        httpd.server_close()


if __name__ == '__main__':
    main()
