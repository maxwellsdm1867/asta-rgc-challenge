# SUBMISSION.md field skeleton

Copy this into `SUBMISSION.md` and fill each field. Keep every field **short** — it's for judges to
read quickly. Fields marked `[confirm]` are the user's to provide; **never fabricate them**.

```markdown
# <Challenge> — submission form (draft)

Copy each field into the submission form. `[confirm]` fields need your input.

## Project Title
<one line>

## Project Summary  *(short — for judges)*
**Goal.** <what had to be found, from what, with what constraints>
**Result.** <the model/answer + headline held-out metric(s); point to the report + data for detail>
**Time.** <ballpark HUMAN time AND COMPUTE time — distinguish the real research effort (e.g. a
multi-year experimental project, mostly data collection, plus months of analysis) from the agent run
(minutes of compute)>

## Reflections  *(what went well / what went badly)*
- Went well: <grounded, specific>
- Went badly / lessons: <grounded in real wrong turns this session>

## Name(s) of people involved
[confirm] — <identities visible in the environment for the user to pick: git author, CLI login>.
The research agent was <model>.

## Email for communication
[confirm] — <candidate emails seen in the environment>.

## (optional) Supporting file(s) for judges
- **trace.tar.gz** — full conversation trajectory (challenge-accepted format); UPLOAD THIS.
- <rendered report URL> · <rendered brief URL / Artifact> · SKILLS_FEEDBACK.md (+ FEEDBACK_AUDIT.md).

## (optional) Pointer to final research environment
<repo URL> (+ rendered-pages URL if Pages is enabled).
```

Reminders:
- The **Time** field is the one most often gotten wrong — separate the human research timeline from
  the agent's compute time, and mark unverifiable figures `[confirm]`.
- List `trace.tar.gz` explicitly as an upload; it's what makes the whole submission verifiable.
- Blind challenge? Note that the repo/pages shouldn't be public until grading unless the owner says so.
