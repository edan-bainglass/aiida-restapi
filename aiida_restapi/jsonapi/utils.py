"""JSON:API utilities."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

CacheBucket = dict[str, tuple[t.Union[str, int], str, dict[str, t.Any], dict[str, t.Any]]]


@dataclass
class IncludedItemParamsCache:
    """Per-request cache for the parameter of an included resources.

    The cache is used to avoid recomputing the parameters of shared included resources (user, computer, etc.).
    The cache is organized in buckets per resource type and maps to id: (id, type, attributes, foreign fields).
    """

    buckets: dict[str, CacheBucket] = field(default_factory=dict)

    def bucket(self, resource_type: str) -> CacheBucket:
        """Get the cache bucket for a given resource type.

        :param resource_type: The resource type.
        :type resource_type: str
        :return: The cache bucket for the resource type.
        :rtype: CacheBucket
        """
        try:
            return self.buckets[resource_type]
        except KeyError:
            bucket: CacheBucket = {}
            self.buckets[resource_type] = bucket
            return bucket
