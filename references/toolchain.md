# Toolchain

Choose tools for what each shot needs to look like. The installed tool, the one mentioned first, and the one used last time are not reasons. Write the choice and the reason in the treatment's **Toolchain** field. If you compromise because a tool is missing or too slow, write that down too.

## What each tool is best at

| Need | Strongest choice | Why |
|---|---|---|
| Light, shadow, material, depth of field, real camera moves, physical objects | **Blender** (Eevee for speed, Cycles for final light) | A real renderer: bounce light, reflections, lens blur and motion blur that 2D tools fake |
| Kinetic typography, UI, product screens, layout-driven scenes | **HyperFrames** or **Remotion** | Real fonts, crisp vector type, CSS or React layout, exact frame timing |
| Data-driven or programmatic scenes, many variants, React components | **Remotion** | Components, props, `interpolate` and `spring`, and `@remotion/three` for simple 3D inside React |
| Fast iteration on HTML motion, catalogue blocks, shaders, audio mixing in the timeline | **HyperFrames** | Its workflows and catalogue carry real motion craft; use them rather than hand-building |
| Assembly, audio mix, loudness, encode, embedding existing footage | **ffmpeg** | Exact, scriptable, and verifiable |

## Combinations

The best-looking code-built films usually combine tools:

- **Blender plates + typographic edit.** Render the camera move or object shot from Blender as a PNG sequence or ProRes 4444 with alpha. Composite type, UI and the edit in HyperFrames or Remotion. The picture gets real light, and the type stays razor sharp.
- **Screen capture + 3D stage.** Put the product UI on a surface in Blender for a hero shot. Keep flat UI sequences in HyperFrames or Remotion for legibility.
- **Separate sound.** Build the music and the effects as their own mix and master them with ffmpeg to the delivery spec, whatever tool made the picture.

Keep one timing source: the score in seconds. Every tool maps from it (see `adapters/`).

## Cost and time

- Blender with Cycles can take minutes per frame. Use Eevee, or Cycles at low samples, for the style frames and the animatic. Render the final overnight or at reduced samples with denoising. Say what the final setting was.
- HyperFrames and Remotion renders take seconds to minutes. They cost little to iterate on.
- If the quality bar needs a slow tool, the time is worth it for the hero shots. Put the slow tool where the camera and the light carry the idea, not everywhere.

## Keep each tool's craft

When a tool has its own workflow skills (HyperFrames' `motion-graphics`, Remotion's agent skills, a Blender MCP), use their building and motion craft. Replace only their intake and storyboard with this skill's plan. Never hand-build to avoid a workflow's planning step: that throws away the renderer's craft. In the first test of this skill, doing exactly that produced a clearer idea with flatter motion than the plain workflow managed.
