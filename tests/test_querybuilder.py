"""Test the /querybuilder endpoint"""

import pytest
from aiida import orm
from fastapi.testclient import TestClient


@pytest.mark.usefixtures('default_nodes')
def test_querybuilder_all(client: TestClient):
    """Test a simple QueryBuilder request."""
    response = client.post(
        '/querybuilder',
        json={
            'path': [
                {
                    'entity_type': 'data.core.base.',
                    'orm_base': 'node',
                    'tag': 'nodes',
                },
            ],
        },
    )
    assert response.status_code == 200, response.text
    assert len(response.json()['data']['attributes']['results']) == 4


@pytest.mark.usefixtures('default_nodes')
def test_querybuilder_full(client: TestClient):
    """Test QueryBuilder result with full response."""
    response = client.post(
        '/querybuilder?flat=true&full=true',
        json={
            'path': [
                {
                    'entity_type': 'data.core.int.Int.',
                    'orm_base': 'node',
                    'tag': 'integer',
                },
            ],
        },
    )
    assert response.status_code == 200, response.text
    result = response.json()['data']['attributes']['results'][0]['integer']
    assert 'attributes' in result
    assert 'value' in result['attributes']
    assert result['attributes']['value'] == 1
    assert 'extras' in result
    assert 'repository_metadata' in result


def test_querybuilder_node_in_group(client: TestClient, default_nodes: list[str], default_groups: list[str]):
    """Test a QueryBuilder request filtering integers by group membership."""
    node = orm.load_node(default_nodes[0])
    group = orm.load_group(default_groups[0])
    group.add_nodes(node)
    response = client.post(
        '/querybuilder?flat=true',
        json={
            'path': [
                {
                    'entity_type': 'group.core.',
                    'orm_base': 'group',
                    'tag': 'group',
                },
                {
                    'entity_type': 'data.core.int.Int.',
                    'orm_base': 'node',
                    'joining_keyword': 'with_group',
                    'joining_value': 'group',
                    'tag': 'node',
                },
            ],
            'filters': {
                'group': {
                    'pk': group.pk,
                }
            },
            'project': {
                'group': [
                    'label',
                ],
                'node': [
                    'pk',
                    'attributes.value',
                ],
            },
        },
    )
    assert response.status_code == 200, response.text
    result = response.json()['data']['attributes']['results']
    assert result == [
        {
            'group': {
                'label': group.label,
            },
            'node': {
                'pk': node.pk,
                'attributes.value': node.value,
            },
        }
    ]


def _format_time(time: str) -> str:
    """Format a time string to ISO 8601 format with 'Z' suffix for UTC."""
    return time.isoformat().replace('+00:00', 'Z')


def test_querybuilder_result_normalization(client: TestClient, default_nodes: list[str], default_groups: list[str]):
    """Test the normalization of QueryBuilder results."""
    node = orm.load_node(default_nodes[0])
    group = orm.load_group(default_groups[0])
    group.add_nodes(node)
    response = client.post(
        '/querybuilder?flat=true',
        json={
            'path': [
                {
                    'entity_type': 'group.core.',
                    'orm_base': 'group',
                    'tag': 'group',
                },
                {
                    'entity_type': 'data.core.int.Int.',
                    'orm_base': 'node',
                    'joining_keyword': 'with_group',
                    'joining_value': 'group',
                    'tag': 'node',
                },
            ],
            'filters': {
                'group': {
                    'pk': group.pk,
                }
            },
            'project': {
                'group': [
                    '*',
                ],
                'node': [
                    '*',
                ],
            },
        },
    )
    assert response.status_code == 200, response.text
    result = response.json()['data']['attributes']['results']
    assert result == [
        {
            'group': {
                'pk': group.pk,
                'uuid': str(group.uuid),
                'type_string': group.type_string,
                'label': group.label,
                'description': group.description,
                'time': _format_time(group.time),
                'user': group.user.id,
            },
            'node': {
                'pk': node.pk,
                'uuid': str(node.uuid),
                'node_type': node.node_type,
                'label': node.label,
                'description': node.description,
                'ctime': _format_time(node.ctime),
                'mtime': _format_time(node.mtime),
                'user': node.user.id,
            },
        }
    ]
