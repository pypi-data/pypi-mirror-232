import pytest

from mara_storage.compression import compressor, uncompressor, Compression

def test_get_compressor():
    assert 'cat', uncompressor(Compression.NONE)

    assert 'cat', uncompressor('none')

    assert 'cat', uncompressor(None)

    assert 'cat', uncompressor('nnnndas')
