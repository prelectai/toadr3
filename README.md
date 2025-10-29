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
- List programs [GET]
  - Filter by target type and target values
  - Limit and skip for pagination
- List reports [GET]
  - Filter by program id
  - Filter by event id
  - Filter by client name
  - Limit and skip for pagination
- List subscriptions [GET]
  - Filter by program id
  - Filter by client name
  - Filter by target type and target values
  - Filter by objects
  - Limit and skip for pagination
- Create a report [POST]
- Create a subscription [POST]
- Create a report object based on an initial event

## Example
A small example of how to list programs and events and create a report:

```python
import asyncio
import aiohttp
import toadr3


QA_OAUTH_CONFIG = toadr3.OAuthConfig(
    token_url="",          # URL to the OAuth2 token endpoint
    grant_type="",         # OAuth2 grant type
    claims={"scope": ""},  # OAuth2 claims, for example 'scope'
    client_id="",          # OAuth2 client ID or set to None use environment variable
    client_secret="",      # OAuth2 secret or set to None use environment variable
)

VTN_URL = ""  # URL to the VTN

async def main():
  async with toadr3.ToadrClient(vtn_url=VTN_URL, oauth_config=QA_OAUTH_CONFIG) as client:
    programs = await client.get_programs()
    for program in programs:
      print(f"Program: ID={program.id}, Name={program.program_name}")
        
    events = await client.get_events()
    for event in events:
      print(f"Event: ID={event.id}, Name={event.event_name}, Date={event.created_date_time}")

    report = toadr3.models.Report.create_report(
      event=events[0],
      client_name="ReadmeClient",
      report_type="README_REPORT",
      report_values=[True],
    )

    try:
      result = await client.post_report(report)
      print(f"Report created with ID={result.id}")
    except toadr3.ToadrError as e:
      print(f"ToadrError: {e}")
 


if __name__ == '__main__':
  asyncio.run(main())
```