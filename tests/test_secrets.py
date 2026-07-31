from unittest import mock
import os
import json

import pytest

from app.secrets import SecretManager


def test_secret_manager_env_priority(monkeypatch, tmp_path):
    # Ensure env overrides local file
    sample = tmp_path / "local_secrets.json"
    sample.write_text(json.dumps({"FOO": "local"}))

    monkeypatch.setenv('VAULT_ADDR', '')
    monkeypatch.setenv('VAULT_TOKEN', '')
    monkeypatch.setenv('FOO', 'env')

    # point SecretManager to the local file by modifying its _load_local behavior
    sm = SecretManager()
    sm._local = {"FOO": "local"}

    assert sm.get('FOO') == 'env'


def test_secret_manager_local_fallback(monkeypatch):
    monkeypatch.delenv('VAULT_ADDR', raising=False)
    monkeypatch.delenv('VAULT_TOKEN', raising=False)
    monkeypatch.delenv('FOO', raising=False)

    sm = SecretManager()
    sm._local = {"FOO": "local"}
    assert sm.get('FOO') == 'local'


def test_get_page_token(monkeypatch):
    sm = SecretManager()
    sm._local = {"PAGE_TOKEN_1": "tok123"}
    assert sm.get_page_token('1') == 'tok123'
