# coding=utf8

import os

import pytest

from geektime_dl.data_client.gk_apis import GkApiClient


@pytest.fixture
def gk() -> GkApiClient:
    account = os.getenv('account')
    password = os.getenv('password')
    return GkApiClient(account=account, password=password)
