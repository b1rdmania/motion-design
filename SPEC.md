# motion-design: v1 spec

Author: Andy Bird. Version 3, 27 September 2026. Incorporates review of provider dependencies, creative restrictions and checker uncertainty.

## Purpose

Help a coding agent decide what a film should communicate, hand that plan to a renderer, and inspect the output. This skill plans and reviews; it does not render or prescribe a house style. Artistic improvement must be demonstrated by films, not inferred from the existence of planning files.

## Operation boundaries

Planning and qualitative critique have no tool dependency. Automated review uses Python, NumPy, Pillow, FFmpeg and ffprobe; building needs only the selected renderer. Audio providers and sibling skills are optional. Installation and optional analyser requirements live in `references/dependencies.md`.

Review existing work without restarting the creative process. For a new film, read existing positioning/brand/brief and ask only unresolved material questions. Continue within authorization; user approval gates are opt-in or attached to a material unanswered decision.

The usual full path is treatment/evidence → timed score → representative style frames → moving draft → final review → delivery. Select stages by complexity and uncertainty rather than duration alone. Reviews are internal unless requested otherwise. The default final revision budget is two rounds; report unresolved findings at the limit.

## Contract

The plan comprises `treatment.md`, `score.json` and `evidence.json`; its version hashes all three. The reference files are the authoritative field definitions rather than a second schema here:

- `references/treatment.md`: audience, idea, feeling, brand, ending, boundaries and delivery; concepts/references/motion vocabulary when useful, without mandatory quotas.
- `references/evidence.md`: facts, inferences and metaphors, sources, permitted wording and limits. Source-field completeness is not truth verification.
- `references/score.md`: seconds-based beat and cue timing, readable intervals, edit mechanisms and continuity relationships, sound and mandatory commitments. Supports continuing motion and multiple text/sound cues; legacy super/transition strings remain accepted.

Material plan changes are recorded amendments, followed by a new review. Routine implementation choices do not need formal approval. The plan must not be changed solely to hide a failure.

## Review and receipts

`references/review.md` defines the process. Findings use pass/fail/needs_review/not_applicable. Integrity, communication, evidence, sound integrity and fidelity can block a clear receipt. Uncertain cut, silence and onset detection prompts inspection; it does not prove failure. Craft advice is optional, uncalibrated and non-blocking.

Reading-time calculations are labelled as plan checks. Actual text timing, legibility, implied claims and sound need inspection. A cue list is not listening. Each critique records the render hash and plan version. Original script observations remain intact; `resolve.py` adds separate reviewer decisions and refreshes counts. `deliver.py` recomputes effective status and reports only results and inspection evidence actually recorded. A mismatch or open blocking finding returns non-zero while still writing an honest report.

Scripts:

- `frames.py`: samples hold/text intervals and transition boundaries; contact sheets plus individual frames.
- `motion_strip.py`: pixel activity, candidate cuts and still runs; not pacing quality.
- `audio_check.py`: loudness, peaks, channel-energy silence and rough onsets.
- `check.py`: coordinates automated review and prompts inspection.
- `resolve.py`: records decisions without overwriting observations.
- `deliver.py`: binds the report to the reviewed files and lists limitations.

No beat analyser is bundled. External analysis requires an exact upstream revision, verified licence/notices and tested interface before adoption. Manual cue points always remain valid.

## Renderer boundaries

The agent follows the user's tool choice, preserves a suitable existing project, or selects its own available workflow. Existing video skills and direct coding are valid; no specific renderer is preferred by this skill. Reuse their planning artifacts rather than duplicating intake. Optional adapters illustrate mappings to HyperFrames, Remotion and Blender and do not exclude other tools or combinations. They do not impose entrance-then-freeze staging. Match cuts may be instantaneous; overlapping sequences are used only for edit mechanisms that need them. Audio can be mixed with available renderer tools or externally; muxing must preserve planned picture duration.

Each adapter retains an explicit fixture status. The FFmpeg-generated timing fixture tests the review scripts; it does not prove the three adapters work. Run the five-second fixture through each real renderer before marking it tested. This revision does not claim those runs have occurred.

## Proof plan

1. Preserve the first real test run and report where the skill helps or obstructs it.
2. Produce the same brief with and without the skill, using the same model, assets and comparable effort. Keep the baseline honest. Evaluate comprehension, brand fit, readability and preference with a reviewer who does not know which is which; automated craft metrics alone cannot establish improvement.
3. Run a contrasting brief through the same renderer. If both become the same template, revisit the guidance.
4. Validate actual renderer adapters against the timing fixture, separately from the creative experiment.
5. Run an available skill-auditor when ready, reporting any unavailable tooling rather than treating it as a planning dependency.

Out of scope: AI video generators, character animation, UI micro-interactions, multi-agent orchestration, a style library, or full proof films in every renderer. No paid audio provider is required.
