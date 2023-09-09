from Report import Report
import sys
from dotenv import load_dotenv

load_dotenv()


def main():

    # get sys

    report = Report(f"")
    report.save_report()