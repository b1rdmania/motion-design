# Blender adapter

Blender builds the film in 3D, through `bpy` scripts or a Blender MCP server. Sound is mixed and muxed with ffmpeg after the picture render.

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
    # key the beat's move from start to build, then hold: no keys between build and the beat's end
```

| Score | Blender |
|---|---|
| `beats[i]` | a camera and object state keyed from `f(start)` to `f(start + build)` |
| `transition_in: cut` | camera markers (`timeline_markers` bound to cameras) at `f(start)` |
| `match` / `morph` | a shared object carried across the boundary; no cut marker |
| `motion.hold` | no keys during the hold; use constant or eased-out interpolation into it |
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
ffmpeg -i renders/final_0001-<end>.mp4 -i audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest renders/final.mp4
```

The encoder output filename depends on the frame range. Check the real name before muxing.
