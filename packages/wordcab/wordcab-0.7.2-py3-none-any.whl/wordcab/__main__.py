# Copyright 2022-2023 The Wordcab Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line interface."""
import asyncio
from functools import wraps

import click

from .login import cli_login, cli_logout


def coroutine(f) -> asyncio.coroutine:
    """Decorator to run a function as a coroutine."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.version_option()
def main() -> None:
    """Wordcab Python SDK."""
    pass


@click.command()
def login() -> None:
    """Prompt the user for API credentials and store them as git credentials."""
    cli_login()


@click.command()
def logout() -> None:
    """Remove stored git credentials."""
    cli_logout()


main.add_command(login)
main.add_command(logout)

try:
    from .live import cli_live

    @click.command()
    @click.option(
        "--server-url",
        "-s",
        default="ws://localhost:5001/api/v1/live",
        help="Wordcab API Live server URL",
    )
    @click.option(
        "--source-lang",
        "-l",
        default="en",
        help="Source language of the audio",
    )
    @click.option(
        "--api-key",
        "-k",
        default=None,
        help="Wordcab API Key",
    )
    @coroutine
    async def live(server_url: str, source_lang: str, api_key: str) -> None:
        """Transcribe audio in real-time."""
        await cli_live(server_url, source_lang, api_key)

    main.add_command(live)

except ImportError:
    pass


if __name__ == "__main__":
    main(prog_name="wordcab")  # pragma: no cover
