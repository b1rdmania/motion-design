# Optional tool setup

Use this reference only after choosing a tool that is missing. It is a menu, not a checklist: preserve a working project and the agent's existing capabilities. Installing a renderer, installing an agent skill, and connecting a hosted service are different operations.

The links and starter commands below were checked against official documentation on 27 September 2026. Recheck platform requirements and installed-version help when using them. These commands document setup; they are not an instruction to install everything or make a paid API request. Keep existing project versions; record new versions in the project's normal dependency files.

## Remotion — React video renderer

Use when a React-based composition suits the project. Requires a supported Node.js/runtime and operating system; consult the [official installation guide](https://www.remotion.dev/docs/) for current requirements, templates and licence links.

For a new project, start the interactive scaffold:

```sh
npx create-video@latest
```

In the generated project, install its dependencies with the selected package manager if needed, then run its preview command (normally `npm run dev`). Confirm the supplied composition previews before building the film.

Agent guidance is separate and optional. Remotion's installation guide documents `npx remotion skills add`; use it only if those skills are useful and absent. Review the installation scope rather than replacing an existing workflow. For an existing project, follow the guide's existing-project route instead of scaffolding over it.

## HyperFrames — HTML video renderer

Use when HTML composition fits the project. The [official project](https://github.com/heygen-com/hyperframes) and [CLI reference](https://github.com/heygen-com/hyperframes/blob/main/docs/packages/cli.mdx) document runtime requirements, initialization and local rendering.

No global CLI installation is necessary:

```sh
npx hyperframes init my-video
cd my-video
npx hyperframes doctor
npx hyperframes preview
```

Confirm diagnostics and preview before building. Read `npx hyperframes init --help` for the installed version's options, including skill installation controls; scaffolding may offer or install agent guidance. Choose that deliberately rather than letting it silently replace another workflow.

The official project also documents `npx skills add heygen-com/hyperframes` for optional agent skills. Their installation is distinct from having a working CLI. Neither is required when another video workflow is already suitable.

## ElevenLabs — optional hosted audio service

This is a service connection, not a video renderer. Choose it only when its audio capabilities suit the brief; supplied audio, recordings, other providers and silent films remain valid.

Follow the [official API quickstart](https://elevenlabs.io/docs/eleven-api/quickstart/). API use requires an account and API key. Within the chosen project's Python virtual environment:

```sh
python -m pip install elevenlabs
python -c "from elevenlabs.client import ElevenLabs; print('SDK import OK')"
```

The import check makes no generation request. Configure `ELEVENLABS_API_KEY` through the project's secret mechanism; do not put credentials in the score, repository or logs. A successful import does not verify account access. Use a small generation request only when audio generation and its usage cost are authorized.

The quickstart also covers other SDK/CLI choices and optional agent skills. Do not require Python, ElevenLabs skills or this provider when the project already has a suitable audio workflow.

## Review tools

The local review scripts have their own [dependency setup](dependencies.md). Those requirements do not imply installing any of the three tools above. Tool-specific account terms and licences remain separate from this skill's MIT licence.
