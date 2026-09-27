# Timing fixture

A 5-second test for renderer adapters. The shape:

- 640×360, 24 fps, 5.0 s.
- Three flat plates, with hard cuts at 1.5 s and 3.5 s.
- A tone under the whole film, with a silence from 2.5 to 3.0 s.

Each adapter must render this from `score.json` in its own renderer. Then run:

```
python3 scripts/check.py --plan fixtures/timing --video <render>.mp4 --stage animatic --out /tmp/fixture-review
```

The `fidelity.cut` and `fidelity.silence` findings must all pass (±2 frames).

`make_reference.sh` builds the same timeline with ffmpeg alone. The test suite uses it to check the scripts themselves.

`--shift N` moves the second cut by N frames, so the tests can prove that a late cut fails.
