# Constitution — Team WARPDRIVE (NASA Space Apps 2026, "Field Shift")

Version 1.0 · Adopted 14 November 2026 · Short on purpose. Every spec, plan and line of code must respect it.

## Core principles

1. **Simplicity first.** Between two solutions that meet the spec, choose the simpler one. Add complexity only when the simple version fails and the failure is documented.
2. **No phantom scope.** Build only what the approved spec says. New ideas are written down as "Proposed" and wait for team approval.
3. **Verifiable by a non-technical person.** Every success criterion can be checked by using the app, without reading code.
4. **Respect user data.** The app asks only for crop and location. No names, phone numbers or accounts. No keys or secrets in the code.
5. **Raw data as received.** NASA data is used as delivered. Gaps and missing values are shown, never silently filled. Every correction (e.g., elevation adjustment of temperature) is documented.
6. **Visible reliability.** Next to every result the app shows: data source, period, spatial resolution and confidence level.
7. **Honest uncertainty.** No recommendation is presented as a certainty. The tool supports, and never replaces, the farmer and local agricultural experts. Every strategy lists its information gaps and risks.
8. **Decide before building.** Open questions are resolved and written down before implementation. Nothing is assumed by default.

## Project constraints

- All judge-facing content (app, README, docs, form, video subtitles) is in **English**.
- At least one **NASA dataset is a core input**, not decoration.
- Use of AI ("SI") is disclosed: AI-assisted files carry an "SI disclosure" note; AI images/video carry a visible watermark; no NASA logos or branding.
- No images, voices or likeness of people under 18.
- The demo must work from data stored in the repository (CSV), so it does not depend on live APIs during judging.

## Workflow

Constitution → Spec → Clarify (open questions) → Plan → Tasks → Implement. One integrator merges to `main`. Each role works in its own folder.
