# motion-design

A Claude Code skill that plans a video before it is built and reviews the render after. It does not render. It gives a plan to HyperFrames, Remotion or Blender, and it examines the mp4 that comes back.

**Status: in development.** The v1 plan is in [SPEC.md](SPEC.md). The review scripts and the timing fixture work. The skill text and the renderer adapters are not written yet.

## What it will do

1. Ask four questions: who watches, what they should remember and do, what they should feel, and what the video will not do.
2. Write a treatment: one proposition, a refusal, the last beat first, named references, a motion vocabulary and an evidence ledger.
3. Write a timed score in seconds, which any renderer can use.
4. Review style frames, then a low-resolution animatic, then the final render.
5. Deliver the render with every open finding listed.

## Review scripts

The scripts need ffmpeg and Python 3 with numpy and Pillow. They do not call a model.

```
python3 scripts/check.py --plan plan/ --video render.mp4 --stage final --out review/final-r1 --view-width 375
python3 scripts/deliver.py --plan plan/ --video render.mp4 --critique review/final-r1/critique.json --out DELIVERY.md
```

`check.py` writes `critique.json`. Each finding is `pass`, `fail`, `needs_review` or `not_applicable`. Only findings for integrity, communication, evidence, sound integrity and fidelity to the plan can block delivery. Craft defaults are advice, and the plan can override them.

## Tests

```
python3 -m pytest tests
```

## Licence

MIT.
