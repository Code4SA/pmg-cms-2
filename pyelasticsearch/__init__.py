from pyelasticsearch.client import ElasticSearch
from pyelasticsearch.exceptions import (Timeout, ConnectionError,
                                        ElasticHttpError,
                                        InvalidJsonResponseError,
                                        ElasticHttpNotFoundError,
                                        IndexAlreadyExistsError)

__author__ = 'Erik Rose'
__all__ = ['ElasticSearch', 'ElasticHttpError', 'InvalidJsonResponseError',
           'Timeout', 'ConnectionError', 'ElasticHttpNotFoundError',
           'IndexAlreadyExistsError']
__version__ = '0.7.1'
__version_info__ = tuple(__version__.split('.'))

get_version = lambda: __version_info__
