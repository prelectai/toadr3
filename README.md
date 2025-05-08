[![Toadr3](https://github.com/prelectai/toadr3/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/prelectai/toadr3/actions/workflows/test.yml)
[![Publish to PyPI](https://github.com/prelectai/toadr3/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/prelectai/toadr3/actions/workflows/publish.yml)
[![image](https://img.shields.io/pypi/v/toadr3?label=pypi)](https://pypi.python.org/pypi/toadr3)
[![Python Versions](https://img.shields.io/pypi/pyversions/toadr3)](https://pypi.python.org/pypi/toadr3)
[![image](https://img.shields.io/pypi/l/toadr3.svg)](https://github.com/prelectai/toadr3/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

# toadr3

## Tiny OpenADR3 Python Library

This Python library is a tiny OpenADR3 library that can be used to perform a minimal set of
operations towards a VTN.

Currently, it supports the following operations:

- List events [GET]
  - Filter by program id
  - Filter by target type and target values
  - Limit and skip for pagination
- List reports [GET]
  - Filter by program id
  - Filter by event id
  - Filter by client name
  - Limit and skip for pagination
- Create a report [POST]
- Create a report object based on an initial event

## Example
A small example of how to list events and reports from a VTN:

```python
import asyncio
import aiohttp
import toadr3

TOKEN_URL = ""  # URL to the OAuth2 token endpoint
GRANT_TYPE = ""  # OAuth2 grant type
SCOPE = ""  # OAuth2 scope
CLIENT_ID = ""  # OAuth2 client ID or set to None use environment variable
CLIENT_SECRET = ""  # OAuth2 client secret or set to None use environment variable

VTN_URL = ""  # URL to the VTN


async def main():
  async with aiohttp.ClientSession() as session:
    token = await toadr3.acquire_access_token(
      session, TOKEN_URL, GRANT_TYPE, SCOPE, CLIENT_ID, CLIENT_SECRET
    )

    events = await toadr3.get_events(session, VTN_URL, token)

    for event in events:
      print(f"Event ID: {event.id} - {event.event_name}")

    reports = await toadr3.get_reports(session, VTN_URL, token)
    for report in reports:
      print(f"Report ID: {report.id} - {report.report_name}")

    report = toadr3.models.Report.create_report(
      event=events[0],
      client_name="client_name",
      report_type="REPORT_TYPE",
      report_values=[...],
    )
    result = await toadr3.post_report(session, VTN_URL, token, report)


if __name__ == '__main__':
  asyncio.run(main())
```