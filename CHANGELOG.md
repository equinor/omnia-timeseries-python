# Changelog

## Unreleased

- Reuse a pooled HTTP session per `HttpClient`, with configurable `pool_size` and `close()`/context-manager cleanup.

## v1.0.3

- [PR #14](https://github.com/equinor/omnia-timeseries-python/pull/14) - Add support for protobuf data response via `accept` header in data requests