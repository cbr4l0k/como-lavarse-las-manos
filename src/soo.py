from Report import Report
import sys
from dotenv import load_dotenv
import http.server
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="../front", **kwargs)

load_dotenv()


def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python3 main.py <project_name>")
    #     return
    # project_name = sys.argv[1]
    # report = Report(project_name)
    # report.generate_report()
    PORT = 8004
    #
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping the server...")
        httpd.server_close()

if __name__ == '__main__':
    main()
