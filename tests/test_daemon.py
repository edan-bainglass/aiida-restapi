"""Test the /daemon endpoint"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures('stopped_daemon_client')
def test_status_and_start(client: TestClient):
    """Test ``/daemon/status`` when the daemon is not running and ``/daemon/start``."""
    response = client.get('/daemon/status')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is False
    assert results['num_workers'] is None

    response = client.post('/daemon/start')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == 1

    response = client.post('/daemon/start')
    assert response.status_code == 500, response.content


@pytest.mark.usefixtures('stopped_daemon_client')
def test_worker_when_stopped(client: TestClient):
    """Test ``/daemon/worker`` when the daemon is not running."""
    response = client.get('/daemon/worker')
    assert response.status_code == 200, response.content
    assert response.json() == {}


@pytest.mark.usefixtures('started_daemon_client')
def test_worker_when_running(client: TestClient):
    """Test ``/daemon/worker`` when the daemon is running."""
    response = client.get('/daemon/worker')
    assert response.status_code == 200, response.content

    results = response.json()
    assert isinstance(results, dict)
    assert results

    for worker in results.values():
        assert set(worker.keys()) == {'pid', 'mem', 'cpu', 'started'}


@pytest.mark.usefixtures('started_daemon_client')
def test_status_and_stop(client: TestClient):
    """Test ``/daemon/status`` when the daemon is running and ``/daemon/stop``."""
    response = client.get('/daemon/status')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == 1

    response = client.post('/daemon/stop')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is False
    assert results['num_workers'] is None

    response = client.post('/daemon/stop')
    assert response.status_code == 500, response.content


@pytest.mark.usefixtures('started_daemon_client')
def test_status_and_restart(client: TestClient):
    """Test ``/daemon/status`` when the daemon is running and ``/daemon/restart``."""
    response = client.get('/daemon/status')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == 1

    response = client.post('/daemon/restart')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == 1


@pytest.mark.usefixtures('stopped_daemon_client')
def test_increase_and_decrease_when_stopped(client: TestClient):
    """Test ``/daemon/increase`` and ``/daemon/decrease`` when daemon is not running."""
    response = client.post('/daemon/increase')
    assert response.status_code == 500, response.content

    response = client.post('/daemon/decrease')
    assert response.status_code == 500, response.content


@pytest.mark.usefixtures('started_daemon_client')
def test_increase_and_decrease_when_running(client: TestClient):
    """Test ``/daemon/increase`` and ``/daemon/decrease`` when daemon is running."""
    response = client.get('/daemon/status')
    assert response.status_code == 200, response.content
    initial_workers = response.json()['num_workers']

    response = client.post('/daemon/increase')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == initial_workers + 1

    response = client.post('/daemon/decrease')
    assert response.status_code == 200, response.content

    results = response.json()
    assert results['running'] is True
    assert results['num_workers'] == initial_workers
