# Dependencies by operation

Planning and qualitative critique have no renderer or Python dependency. Do not demand API credentials or install unrelated tools to write a treatment.

Automated review needs FFmpeg and ffprobe on PATH, Python 3.12, NumPy and Pillow. The regression suite additionally uses pytest and Bash; its reference encoder requires FFmpeg's libx264 and AAC encoders. Other Python versions are not yet tested.

From the skill directory, create an isolated environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-review.txt
ffmpeg -version
ffprobe -version
.venv/bin/python -c "import numpy, PIL"
# tests only:
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
```

The requirements files pin the versions tested for this revision. They do not install a renderer or any paid service. For existing supported environments, avoid replacing unrelated packages; use isolation or report compatibility limits.

Only the chosen renderer is needed to build. HyperFrames, Remotion and Blender integrations are optional and their adapters state fixture status. Use installed renderer skills when present, otherwise the renderer's documentation. `/media-use` and `/hyperframes-audio` are optional integrations, not names assumed to exist everywhere.

## Optional beat analysis

Manual cue points are the portable default. A user-provided audiomap can be passed to `check.py --audiomap ...` with `beats_sec: [seconds, ...]` and/or `phrases: [{start: seconds}, ...]`. Rhythm hints are opt-in in the score.

No external beat analyser is bundled, downloaded or licensed by this skill. Before importing an analyser such as HyperFrames' `analyze-beatgrid.py`, record its exact upstream URL/revision, verify that file's licence and notices, identify its Python dependencies (which may include librosa), and test its output against the audiomap contract. Do not represent an unverified licence assertion as established compatibility. Missing analysis never blocks a film: write phrase/cue points manually.
