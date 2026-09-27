# Blender adapter

Blender builds the film in 3D, through `bpy` scripts or a Blender MCP server. Sound can use the chosen native or external workflow; the FFmpeg recipe below is an optional external-mix path.

**Fixture status: not yet run.**

## Mapping

```python
import bpy, json
score = json.load(open(bpy.path.abspath("//plan/score.json")))
fps = score["fps"]
scene = bpy.context.scene
scene.render.fps = fps
scene.frame_start = 1
scene.frame_end = round(score["duration"] * fps)

def f(seconds):
    return 1 + round(seconds * fps)   # timeline starts at frame 1

for b in score["beats"]:
    start, build = f(b["start"]), f(b["start"] + b.get("motion", {}).get("build", 0))
    # key the reveal; readability during hold does not require freezing all objects/cameras
```

| Score | Blender |
|---|---|
| `beats[i]` | a camera and object state keyed from `f(start)` to `f(start + build)` |
| `transition_in: cut` | camera markers (`timeline_markers` bound to cameras) at `f(start)` |
| `match` / `morph` | a match may use a camera cut preserving a visual relationship; a morph may carry geometry continuously |
| `motion.hold` | keep essential information readable; camera and secondary objects may remain animated |
| `super` | text objects, or composite supers later in HyperFrames or Remotion |

## Renders for each stage

```
# style frames: one still per beat
blender -b film.blend -o //renders/style/b1_ -F PNG -f <frame>
#   rename to renders/style/<beat-id>.png

# animatic: Eevee, 50% resolution, low samples
blender -b film.blend --python-expr "import bpy; s=bpy.context.scene; s.render.resolution_percentage=50; s.eevee.taa_render_samples=8" \
  -o //renders/animatic_ -F FFMPEG -a

# final
blender -b film.blend -o //renders/final_ -F FFMPEG -a
```

Then mux the mix (see `references/sound.md`) and review the muxed file:

```
# Set film_duration from score.json; pad/trim audio, never truncate picture.
film_duration=30
ffmpeg -i renders/final_0001-END.mp4 -i audio/mix.wav -filter_complex \
  "[1:a]apad,atrim=duration=${film_duration}[a]" \
  -map 0:v -map '[a]' -c:v copy -c:a aac renders/final.mp4
```

The encoder output filename depends on the frame range. Check the real name before muxing.

Read `transition_in.type` for the edit mechanism and `relationship` for visual continuity. Legacy `match:<property>` means a cut with a relationship, not a compulsory dissolve. Keep total duration fixed when adding overlap. Use the intended delivery size for each composition and review each final format.

## Quality

Blender is the tool for light, material, depth and a real camera. Use it where those carry the idea.

- **Eevee** for style frames and the animatic. **Cycles** with denoising for final hero shots when bounce light, glass or fog matter. Record the samples and render time in the treatment.
- Turn on depth of field and motion blur deliberately. They are most of what separates a rendered shot from a 3D preview.
- Blender text is fine for dimensional type. For crisp UI and editorial type, render plates (PNG sequence, or ProRes 4444 with alpha) and composite the type in HyperFrames or Remotion (`references/toolchain.md`).
- Keep the scene in the project (`.blend` plus textures), so the film can be re-rendered and edited.
