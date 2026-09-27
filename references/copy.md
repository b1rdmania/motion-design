# Copy for video

On-screen text and VO. What follows is what experienced copywriters do and why. It is knowledge to decide with, not a blacklist. Break any of it on purpose when the film is better for it.

## The line and the picture

The one rule every source agrees on: **the line says what the picture cannot.**

- If the frame already shows the action, the line usually should not describe it. Give the viewer what the image cannot show: a number, a comparison, a consequence, or a reframe. A super that says "Fast onboarding" over a demo of fast onboarding is redundant twice. A repeated label can still earn its place for accessibility or recognition.
- "Headlines counterpoint the image, directing its interpretation" (Barnaby Benson, "Writing Headlines").
- Proof beats claims. Dave Trott: "Demonstration, not empty claims." Let the image carry the proof, and keep the copy out of its way.
- A fact beats an adjective. D&AD (Vikki Ross): "Anyone can say something is 'amazing', but what's the fact?"
- A line whose only job is to name a feeling ("feel confident") usually means the image has not done its job.
- A film can have no VO. Linear's "Introducing Linear for Agents" has none: cut rhythm and kinetic type carry it.

## Structure

- **Clarity before cleverness.** By about five seconds, the viewer should know the film is for them. By the end, they should know what the thing is (name and a one-line function) and what to do. An intriguing opening only works if it resolves quickly; an abstract hook that never says who "you" is loses the viewer who did not write the brief.
- Writing the last beat first clarifies what the film is for.
- One promise and one proof point is the usual shape of a short film. Three value props in 30 s is typically a structural failure, not a style problem.
- The brand name often lands harder after the hook than before it, but not much after: if the name arrives in the last quarter, check that the viewer knew what they were watching before then. Early branding is a choice, not a fault.
- A CTA can only ask for what the film has earned. A feature tour cannot support "buy now".
- If the film has VO and a tagline, speaking the tagline helps. Ipsos found text-only taglines barely moved perception; the same line voiced did.

## Reading time

| Measure | Value | Source | Status |
|---|---|---|---|
| Comfortable reading speed | ≤ 17 characters per second of hold | Netflix Timed Text Style Guide (17–20 cps adult) | prompt |
| Planned reading-speed gate | 25 cps | above the rate where BBC R&D viewers reported "too fast" (≈ 227 wpm) | **blocks by default**; set `delivery.max_text_cps` to change it |
| Subtitle convention | ≤ 42 characters, ≤ 2 lines | Netflix | subtitles only; not a limit on title cards or kinetic type |
| VO | about 2.5 words per second of film; ~75 words in 30 s | ad practice: write 150, cut to 75 | prompt |

The gate checks the **plan's** timing. It cannot prove the rendered text appeared or was readable; the review checks that on the frames. Audience, type size, familiarity and visual competition all change real reading effort.

Type-led launch films mostly snap or cut their text in, hold it for its reading time, then cut it away, rather than drifting it in slowly from zero opacity.

## Four tests for a line

1. **Generic.** Could this line appear for any product? If so, make it specific.
2. **Read aloud.** Does it sound like a person or a press release?
3. **So what.** Would the viewer think "so what"? If so, add the concrete outcome.
4. **Specific.** Is there a number, a scene or a named detail?

## Familiar phrasing

`check.py` flags stock openers ("Introducing…", "Meet…", "Say goodbye to…", "Imagine a world where…") and filler ("harness the power of", "game-changer", "seamless", "unlock", "next level"). This is a prompt, not a ban. Keep a phrase when it is the best fit; replace it when it is empty or interchangeable.

| Instead of | Try |
|---|---|
| "Introducing X" | open on the problem or the result, and name X once it is earned |
| "Meet X, the all-in-one solution" | the one specific thing it does, with a number |
| "Say goodbye to [pain]" | show the before and after; the line carries only the fact the image cannot |
| "Harness the power of AI" | name the mechanism or the outcome |

After writing, run a plain-English pass on every super and VO line. Cut what does not work.
