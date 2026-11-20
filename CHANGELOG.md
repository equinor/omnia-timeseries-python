# Changelog

## Unreleased

- Add request timeouts and resilient retries with jitter, capped `Retry-After` handling, and safe retries for transient request failures.

## v1.0.3

- [PR #14](https://github.com/equinor/omnia-timeseries-python/pull/14) - Add support for protobuf data response via `accept` header in data requests