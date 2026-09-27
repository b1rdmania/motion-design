# motion-design: v1 spec

Author: Andy Bird. Version 4, 27 September 2026. Version 3 (Codex) made providers optional and the review evidence-based. Version 4 restores discovery and narrative development as the core, the forcing decisions that changed the first test film, a quality bar, and toolchain choice for quality.

## Purpose

Help a user turn a business story, often an unclear one, into a narrative, and that narrative into showreel-quality motion design. Discovery and narrative development are the core. Technical review supports them. The skill does not render or prescribe a house style. Artistic improvement must be shown by films, not inferred from planning files.

## Workflow

1. **Understand the business.** Read the supplied material and collect the real assets (`assets.json`) before asking anything it already answers.
2. **Audience and stakes.** Who watches, why they should care, what should change after they watch, and the tone and placement.
3. **Develop the narrative together.** Two or three structurally different tellings, each with an opening, a progression and an ending in plain language. The user chooses or steers.
4. **Visual treatment.** Composition, typography, references (take and leave), craft, motion, pacing, sound, the lead, and a toolchain chosen per shot for quality. Style frames before the expensive build.
5. **Build** with the strongest workflow available, keeping its motion craft. The plan owns what and when; the tools own how.
6. **Does it land?** Judge the communication and the execution against the bar. Scripts support the judgement.

The questions are central when the story is unresolved and lighter when the user arrives with a clear brief. They do not disappear just because the agent could guess.

## The bar

Showreel quality: the piece a senior motion designer would put first in their reel, or send to audition for an A24 trailer. A standard of craft, not a look.

## Operation boundaries

Planning and qualitative critique have no tool dependency. Automated review uses Python, NumPy, Pillow, FFmpeg and ffprobe; building needs only the selected renderer. Audio providers and sibling skills are optional. Installation and optional analyser requirements live in `references/dependencies.md`.

Review existing work without restarting the creative process. For a new film, read existing positioning/brand/brief and ask only unresolved material questions. Continue within authorization; user approval gates are opt-in or attached to a material unanswered decision.

The usual full path is treatment/evidence → timed score → representative style frames → moving draft → final review → delivery. Select stages by complexity and uncertainty rather than duration alone. Reviews are internal unless requested otherwise. The default final revision budget is two rounds; report unresolved findings at the limit.

## Contract

The plan comprises `treatment.md`, `score.json` and `evidence.json`; its version hashes all three. The reference files are the authoritative field definitions rather than a second schema here:

- `references/treatment.md`: a template. Forcing decisions: tellings considered (unless the user supplied the concept), refusal, last beat first, references with take and leave, craft, and toolchain with reasons. A conjunction is fine when it names one condition. Taste stays in overridable defaults, not rules.
- `references/assets.md`: asset intake from the project (repo, brand doc, font files, SVGs, images) into `assets.json`, with source and licence; fonts loaded from files.
- `references/evidence.md`: facts, inferences, metaphors and samples (mock UI, sample data), sources, permitted wording and limits. Source-field completeness is not truth verification.
- `references/score.md`: seconds-based beat and cue timing, readable intervals, edit mechanisms and continuity relationships, sound and mandatory commitments. Supports continuing motion and multiple text/sound cues; legacy super/transition strings remain accepted.

Material plan changes are recorded amendments, followed by a new review. Routine implementation choices do not need formal approval. The plan must not be changed solely to hide a failure.

## Review and receipts

`references/review.md` defines the process. Findings use pass/fail/needs_review/not_applicable. Integrity, communication, evidence, sound integrity and fidelity can block a clear receipt. Uncertain cut, silence and onset detection prompts inspection; it does not prove failure. Craft advice is optional, uncalibrated and non-blocking.

The planned reading-speed gate (25 characters per second by default, set by `delivery.max_text_cps`) blocks; it is labelled as a plan check. Actual text timing, legibility, implied claims and sound need inspection. A cue list is not listening. Each critique records the render hash and plan version. Original script observations remain intact; `resolve.py` adds separate reviewer decisions and refreshes counts. `deliver.py` recomputes effective status and reports only results and inspection evidence actually recorded. A mismatch or open blocking finding returns non-zero while still writing an honest report.

Scripts:

- `frames.py`: samples hold/text intervals and transition boundaries; contact sheets plus individual frames.
- `motion_strip.py`: pixel activity, candidate cuts and still runs; not pacing quality.
- `audio_check.py`: loudness, peaks, channel-energy silence, rough onsets and low-band (bass) onsets.
- `beatmap.py`: a heuristic audiomap (tempo, grid, onsets, bass entries, energy) with numpy only.
- `check.py`: coordinates automated review and prompts inspection.
- `resolve.py`: records decisions without overwriting observations.
- `deliver.py`: binds the report to the reviewed files and lists limitations.

`beatmap.py` is heuristic and must be checked by ear. Any external analyser requires an exact upstream revision, verified licence/notices and tested interface before adoption. Manual cue points always remain valid.

## Renderer boundaries

The agent follows the user's tool choice, preserves a suitable existing project, or selects its own available workflow. Existing video skills and direct coding are valid. No renderer is preferred by default: the agent chooses per shot for quality (`references/toolchain.md`) and records why. It keeps each workflow's motion craft and replaces only its intake and storyboard. Reuse their planning artifacts rather than duplicating intake. Optional adapters illustrate mappings to HyperFrames, Remotion and Blender and do not exclude other tools or combinations. They do not impose entrance-then-freeze staging. Match cuts may be instantaneous; overlapping sequences are used only for edit mechanisms that need them. Audio can be mixed with available renderer tools or externally; muxing must preserve planned picture duration.

Each adapter retains an explicit fixture status. The FFmpeg-generated timing fixture tests the review scripts; it does not prove the three adapters work. Run the five-second fixture through each real renderer before marking it tested. This revision does not claim those runs have occurred.

## Proof plan

**Test 1 (27 September 2026).** Tidewater sting, same brief, assets and model; the renderer was fixed to HyperFrames by the test brief. The skill run had a stronger idea and better phone legibility. The baseline had more motion craft, and Andy judged it much better overall. Cause: the skill agent hand-built the film to avoid the workflow's planning and lost HyperFrames' motion craft. It also tested autonomous execution, not collaborative discovery.


1. Preserve the first real test run and report where the skill helps or obstructs it.
2. Produce the same brief with and without the skill, using the same model, assets and comparable effort. Keep the baseline honest. Evaluate comprehension, brand fit, readability and preference with a reviewer who does not know which is which; automated craft metrics alone cannot establish improvement.
3. Run a test that begins with business material and an unresolved communication problem, including a real (or simulated) client conversation, with no renderer fixed.
4. Run a contrasting brief through the same renderer. If both become the same template, revisit the guidance.
5. Validate actual renderer adapters against the timing fixture, separately from the creative experiment.
6. Run an available skill-auditor when ready, reporting any unavailable tooling rather than treating it as a planning dependency.

Out of scope: AI video generators, character animation, UI micro-interactions, multi-agent orchestration, a style library, or full proof films in every renderer. No paid audio provider is required.
