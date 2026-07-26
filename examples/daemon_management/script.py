#!/usr/bin/env python
"""Example script to demonstrate daemon management over the web API."""

from __future__ import annotations

import typing as t

import click
import requests

BASE_URL = 'http://127.0.0.1:8000'


def echo_error(message: str) -> None:
    """Echo the message prefixed with ``Error`` in bold red.

    :param message: The error message to echo.
    """
    click.echo(click.style('Error: ', fg='red', bold=True), nl=False)
    click.echo(message)


def request(
    url,
    json: dict[str, t.Any] | None = None,
    data: dict[str, t.Any] | None = None,
    method='POST',
) -> dict[str, t.Any] | None:
    """Perform a request to the web API of ``aiida-restapi``.

    :param url: The relative URL path without leading slash, e.g., `nodes`.
    :param json: A JSON serializable dictionary to send in the body of the request.
    :param data: Dictionary, list of tuples, bytes, or file-like object to send in the body of the request.
    :param method: The request method, POST by default.
    :returns: The response in JSON or ``None``.
    """
    response = requests.request(  # pylint: disable=missing-timeout
        method,
        f'{BASE_URL}/{url}',
        json=json,
        data=data,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        results = response.json()

        echo_error(f'{response.status_code} {response.reason}')

        if 'detail' in results:
            echo_error(results['detail'])

        for error in results.get('errors', []):
            click.echo(error['message'])

        return None
    return response.json()


@click.command()
def main():
    """Manage the daemon over the web API."""
    response = request('daemon/status', method='GET')

    if response['running']:
        num_workers = response['num_workers']
        click.echo(f'The daemon is currently running with {num_workers} workers')

        click.echo('Stopping the daemon.')
        response = request('daemon/stop', method='POST')

    else:
        click.echo('The daemon is currently not running.')
        click.echo('Starting the daemon.')
        response = request('daemon/start', method='POST')
        num_workers = response['num_workers']
        click.echo(f'The daemon is currently running with {num_workers} workers')


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
