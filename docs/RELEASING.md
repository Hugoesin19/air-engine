# Releasing varly

## Prerequisites (one-time)

1. [PyPI account](https://pypi.org/account/register/)
2. **Trusted publishing** for `Hugoesin19/varly`:
   - PyPI → Your project → Publishing → Add GitHub Actions publisher
   - Owner: `Hugoesin19`, repo: `varly`, workflow: `publish.yml`, environment: `pypi`
3. GitHub repo → Settings → Environments → create **`pypi`** (no secrets required with trusted publishing)

Manual fallback: `UV_PUBLISH_TOKEN` from PyPI → `uv publish --token "$TOKEN"`

## Release checklist

1. Update `version` in `pyproject.toml` and `CHANGELOG.md`
2. Run locally:
   ```bash
   uv run pytest
   uv build
   pip install dist/varly-*.whl
   varly verify --demo
   varly try
   ```
3. Commit and push `main`
4. Tag and push:
   ```bash
   git tag -a v1.1.0 -m "v1.1.0: varly try, bundled fixtures, live policy"
   git push origin v1.1.0
   ```
5. GitHub Actions **Publish to PyPI** runs on the tag
6. Create a [GitHub Release](https://github.com/Hugoesin19/varly/releases) from the tag (copy CHANGELOG section)

## Verify PyPI install

```bash
pip install varly==1.1.0
varly verify --demo
varly try
```

Expect `PASS` on `--demo`. `try` runs PASS, FAIL, and regression.

## GitHub Action for consumers

```yaml
- uses: Hugoesin19/varly/.github/actions/verify-trace@v1.0.0
  with:
    trace-file: path/to/run.json
    contract-file: examples/policies/mvp.yaml
    source: capture
```

For in-repo usage, pin to a tag or use `./.github/actions/verify-trace`.
