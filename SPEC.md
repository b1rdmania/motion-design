# motion-design: v1 spec

Author: Andy Bird. Co-builder: Esko (to be added). Version 2, 27 September 2026.
Includes review notes from Codex and Fable. Research: `~/Documents/motion-director-research/README.md`.

## Problem

Code renderers (Remotion, HyperFrames, Blender) now produce technically clean video. The output still reads as generated: it fades up, it centres the text, it lists three features, and it opens with "Introducing…". The model builds before it decides. A creative director, a motion designer and a copywriter decide first.

motion-design is a standalone skill. It makes the decisions before the build and reviews the render after. It does not render. It hands a contract to a renderer and reviews what comes back.

## Principle: decisions, not a house style

The orchestrating agent is already good at craft. The skill will not tell it how a video should look. It makes the agent decide, write the decisions down, and keep to them.

- The treatment and its references set the style. Two briefs with different references should give two different films.
- Craft numbers from the research are **defaults**. The treatment can override any default in one line with a reason.
- Gates check a film against its own plan and against a small set of integrity rules. They do not check it against a house style.
- A check script cannot certify aesthetic quality. Rendered inspection is still necessary, and the report says which checks were measured and which were judged.
- SKILL.md stays short. The research sits in `references/` as the reason behind each default.

## Flow

```
intake → treatment.md → score.json
       → style frames      (review 1: look, legibility at viewing size)
       → animatic          (review 2: timing, cuts, sound continuity; low-res, no polish)
       → final render      (review 3: integrity, fidelity, representative frames)
       → delivery          (unresolved findings listed, never hidden)
```

Each step writes a file. The next step does not start without it. An instruction that only exists as prose does not run (lesson from the Groundnut Lean trial).

Reviews 1–3 are internal by default. The user sees the plan, and then the result. A user who asks for gates gets gates.

**Budget.** Up to two revision rounds on the final render. When the budget is used up, deliver with the open findings marked. Do not declare success. Do not edit the plan to make a failed fidelity check disappear. A plan change is a recorded amendment with a reason.

## Intake

Read any positioning doc, brand system and existing brief first. Then ask only what they do not answer:

1. Who watches this, and where (feed, launch page, keynote, phone)?
2. What should they remember, and what should they do next?
3. What should they feel? One word, or a short progression (for example "intrigue → recognition → confidence").
4. What will this video not do or show?

Also confirm the brand source, the renderer, the aspect ratios and the delivery specification.

Do not call `positioning-products` automatically. Suggest it only if the positioning itself is unresolved.

**Sizing.** A clip under 20 s uses the light path: style frames and final review only. A launch film uses the full path.

## treatment.md

This is the creative contract, one page.

| Field | Rule |
|---|---|
| Proposition | One sentence. If it contains "and", split it and pick one. |
| Audience, placement, next action | From intake. |
| Feeling | One word, or a progression. |
| Refusal | At least one thing the video will not show or claim. |
| Last beat | Written first. |
| Tellings considered | At least two structurally different concepts, with one line on why this one was chosen. |
| References | 2–4 named real works. For each: what to take from it, and what not to take. |
| Motion vocabulary | 2–4 verbs this film uses, each with its meaning. Example: Inspect, Align, Resolve. |
| Lead | `music`, `narration` or `visual`. This sets which track is timed first. |
| Brand | Source file, palette, type, logo source. Mandatory items are marked. |
| Evidence | The ledger lives in `evidence.json`, beside the treatment. |
| Delivery spec | Aspect ratios, sizes, fps, loudness target (default −14 LUFS integrated, −1 dBTP). |
| Overrides | Any default this film breaks, with a reason. |

### Evidence ledger

The plan folder holds `treatment.md`, `score.json` and `evidence.json`. The plan version is a hash of the three files.

`evidence.json` lists the claims. For each claim:

- `id`.
- `type`: `fact`, `inference` or `metaphor`.
- `source`: a URL, dataset, calculation or demonstrated behaviour.
- `evidence`: the supporting excerpt or data.
- `permitted_wording`: what the film is allowed to say.
- `limits`: what the film must not imply.
- `beats`: the beats where the claim appears.

A metaphor is allowed to be unprovable. It must not be presented as a fact. Example: lifted record layers in a film stand for a data join. They do not show that a property is available.

## score.json

This is the timed plan, in seconds, so it works with any renderer.

- `plan_version`: the hash of treatment plus score.
- `lead`, `fps`, `duration`.
- `delivery`: `formats[]` (name, width, height), `view_width`, `loudness_lufs`, `true_peak_dbtp`, and `audio` (true or false).
- `overrides[]`: `{rule, reason}` for any default this film breaks.
- `music`: track, provenance, why it fits (phrase structure, energy, instrumentation, ending), and an optional `audiomap`.
- `beats[]`, each with:
  - `id`, `start`, `dur`.
  - `job`: what the viewer learns.
  - `proves`: an evidence id, or null.
  - `super`: text and reading hold, or null.
  - `vo`: the line, or null.
  - `focal`: the element the eye goes to.
  - `verb`: from the motion vocabulary.
  - `motion`: build and hold duration.
  - `transition_in`: `cut`, `match:<property>` or `morph:<element>`.
  - `sound`: cues, each with a job, and planned silences.
  - `commitments[]`: mandatory items, such as the correct logo or exact copy.
- `events[]`: detectable events only (hard cuts, silences, hits), each with a timestamp. Fidelity checks gate on these.

Beat alignment to music is available, not required. If `lead` is `music`, map the track's phrases before the shots are timed.

## Review

### Sampling

- **Style frames**: one per beat at final size. Each is also viewed at intended viewing width (375 px for phone).
- **Animatic and final**, for each beat:
  - the start of the reading hold
  - the end of the reading hold
  - both sides of each transition
  - any moment a check flagged.
- **Motion strip**: activity per frame and detected cuts. It measures activity. It does not establish good pacing.

### Statuses

Every finding is `pass`, `fail`, `needs_review` or `not_applicable`. An uncertain machine result is `needs_review`. It is never a pass and never an automatic fail.

### Blocking categories

| Category | Can block delivery when | Not applicable when |
|---|---|---|
| Artifact integrity | Output will not decode, media is missing, dimensions, fps or duration are wrong, or the critique does not match the render hash | never |
| Communication | Required text or speech is not understandable at intended viewing size | the film has no text or speech |
| Evidence | A factual claim is unsupported or contradicted, or a metaphor is presented as a fact | the film makes no claims |
| Sound integrity | Clipping, unintended gaps or repeats, unintelligible required speech, or the delivery spec is missed | intentional silence is not a loudness failure |

### Fidelity (can block)

- Declared `events[]` occur within ±2 frames.
- Mandatory `commitments[]` are present.

Morphs, match cuts and holds that the scene-cut detector cannot see are `needs_review`, not fail.

### Defaults (advice only; overridable)

| Default | Starting value |
|---|---|
| Hold ≥ build | per beat |
| No animated beat under 1 s | hard cut instead |
| Pace varies | coefficient of variation ≥ 0.25 |
| Cuts land on phrases | music-led films only |
| Super reading speed | ≤ 17 cps, ≤ 42 chars, ≤ 2 lines |
| VO budget | ≤ 2.5 words/s |
| Stock openers and filler | list in `references/copy.md` |

The starting values come from the research. They are marked **not calibrated** until test briefs have been run.

### critique.json

- `render_sha256` and `plan_version`. A renderer ignores a critique whose hashes do not match.
- `round` and `stage` (`style_frames`, `animatic` or `final`).
- For each finding:
  - `beat` and `t` (the exact timestamp)
  - `rule` and the rule's source
  - `evidence`: measured values, or what was observed
  - `status` and `blocking`
  - `fix`: the suggested correction.
- `unresolved[]`: carried into the delivery note.

## Scripts

These scripts do not call a model. Each one writes a file. `check.py` runs the other three.

| Script | Does |
|---|---|
| `frames.py` | Extracts the review samples from an mp4 and the score. Builds labelled contact sheets. Can downscale to viewing width. |
| `motion_strip.py` | Activity per frame, using ffmpeg frame difference. Detects scene cuts. Outputs CSV and PNG. |
| `audio_check.py` | Loudness and true peak (ebur128), clipping, silences, and gaps. Optional onset map. |
| `check.py` | Runs the three above. Checks the render against the plan. Writes `critique.json` with measured findings and the judged items the agent must resolve. |
| `deliver.py` | Writes `DELIVERY.md`. Exits non-zero if the critique does not match the render or the plan, or if blocking findings are open. |

The agent adds judged findings after it inspects the frames.

HyperFrames' `analyze-beatgrid.py` is Apache-2.0. Music-led projects can use it as an optional import, with credit. The fallback is manual cue points in `score.json`.

## Renderer adapters

The score is in seconds. Each adapter is one reference file that covers:

- how the score maps to that renderer's timeline
- how to render style frames, the animatic and the final
- how the audio gets muxed.

| Renderer | Mapping | Draft render |
|---|---|---|
| HyperFrames | Treatment and score go to `/hyperframes`; beats become compositions with `data-start` | low-res render |
| Remotion | frames = seconds × fps; one `<Sequence>` per beat | `--scale=0.5` |
| Blender | keyframes at seconds × fps through bpy or MCP; audio muxed with ffmpeg | Eevee, low samples, 50% resolution |

A small shared timing fixture tests all three adapters: 5 s, 3 beats, 2 hard cuts, 1 silence. Each renderer must hit the fixture's events within ±2 frames.

## Sound

- The lead decides the order. Music-led: map the track's phrases first. Narration-led: lock the spoken argument and its pauses first. Visual-led: lock the key action first, then build sound around it.
- Choose music for its phrase structure, energy, instrumentation and ending. Tempo alone is not enough. Leo's tempo bands are a starting suggestion.
- A sound effect needs a job: a physical action or a meaningful boundary. Keep tails. Do not use an abrupt gate that clicks.
- Record provenance and credits for every track.
- Mix inside HyperFrames with `hyperframes-audio`. For Remotion and Blender, use ffmpeg: `sidechaincompress` to duck under VO, and `loudnorm` to hit the delivery spec.

## Delivery

- Every render, with its sha256.
- The treatment, the score, and every `critique.json`.
- The evidence ledger and the audio provenance.
- The render commands.
- The unresolved findings.
- Limitations, stated plainly. Professional quality is never claimed by assertion.

## Proof of v1

1. **Timing fixture.** It passes in HyperFrames and Remotion. The Blender adapter ships, marked "fixture-tested" only if it passes.
2. **First real brief: Site DNA.** It has a brief, a claim ledger, assets and known failure cases (see `~/Documents/site-dna/video/codex/v3/`). Make one film, skill-on, in HyperFrames.
3. **Blind judge.** A fresh agent that has not seen either build gets the skill-on and skill-off films unlabelled. Same brief, assets and effort for both. It scores comprehension, brand fit, readability and preference. Esko reviews as a second judge if he is willing. Andy is not the judge.
4. **Not samey, run early.** A second, contrasting real brief (Common or Record Bore) goes through the same renderer. If the two films look alike, the skill is too prescriptive. This runs before any polish.
5. Run `skill-auditor` on the skill.

## Out of scope for v1

- Generative video models (that is shotkit's lane).
- Character animation.
- UI micro-interactions.
- Multi-agent orchestration.
- A style library.
- Full films in all three renderers.

## Build order

1. Repo skeleton, scripts and the timing fixture. These do not depend on any open question.
2. One full loop in HyperFrames on Site DNA: plan → style frames → animatic → final → review.
3. SKILL.md and references, written from what the loop needed.
4. Remotion and Blender adapters, checked against the fixture.
5. Contrasting brief, blind judge, `skill-auditor`.
