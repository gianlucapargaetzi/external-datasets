# external-datasets

Where outside datasets (Hugging Face, git repositories, plain folders) are linked to our tracking and read in
one standard shape. A training script asks for a dataset by name, and optionally a commit of **this** repository:

```python
from clearml.datasets import Dataset
data = Dataset.get_external("example")                       # latest main
data = Dataset.get_external("example", "<commit>")           # a fixed commit
```

The commit fixes both the pin file (where the data comes from) and the adapter code (how it is read). The
source's own revision is the one the script passes, else the pin file's `revision`, else the latest. The run
records the revision, the adapter and this repository's commit.

## Layout

| Path | What |
|---|---|
| `datasets/<name>.yaml` | one pin file per dataset: `source` (`huggingface`, `git`, `local`), `link`, default `adapter`, optional `revision`, optional `overrides` |
| `adapters/<adapter>.py` | one `Adapter` class per file, turning the source's files into the standard shape |
| `tests/` | one test per adapter on a tiny sample of the source |

## Adding a dataset

1. Add `datasets/<name>.yaml`.
2. Write `adapters/<adapter>.py`. Declare the modalities and labels, then call `writer.add(...)` for each sample.
   Boxes are `[x1, y1, x2, y2]` in pixels. See `adapters/example_json_boxes.py`.
3. Copy a tiny sample of the source (a few files) into `tests/data/<adapter>/`. `tests/test_adapters.py` runs
   every adapter on its sample and fails for an adapter without one.
4. Open a pull request. The `adapters` workflow must pass before it can be merged.
5. Scripts that ask for no particular commit use the latest `main`. Use the commit hash to rerun exactly.

## Keeping `main` working

`main` is what runs get when they name no commit, so only pull requests that pass `.github/workflows/test.yml`
may reach it. Set this once in GitHub: Settings, Branches, a rule for `main` that requires a pull request and
the status check `adapters`. The workflow needs a repository secret `CLEARML_SDK_TOKEN` (a read-only token for
the `clearml` fork).

The tests run on the samples in `tests/data/`, not on the real sources, so they prove that the adapter reads
its layout, not that a new upstream revision still has it. When a source changes, a run fails with a message that
names the adapter; add a second adapter and an `overrides` entry for the new revisions.

## When a source changes its layout

The adapter fails with a message that names it. Add a second adapter for the new layout and list the
affected source revisions in the pin file:

```yaml
overrides:
  - revisions: ["9b1c4e7"]     # start of the source revision(s) with the new layout
    adapter: coco_det_v2
```

Old commits of this repository keep reading old revisions with the old adapter.
