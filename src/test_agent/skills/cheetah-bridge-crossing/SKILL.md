---
name: cheetah-bridge-crossing
description: >-
  Estimate how long it takes an animal to cross a man-made structure (e.g. "how
  long for a cheetah to cross the Moskva River via the Bolshoy Kamenny Bridge").
  Use whenever the user asks for the time/duration for a moving creature to
  traverse a bridge, river, road, or similar span. Drives a reason → search →
  compute → self-verify pipeline over web search + code execution.
---

# Crossing-time estimation

You answer questions of the form **"how long does it take <animal> to cross
<structure>?"** by retrieving two facts from the external environment, computing
a time, and then verifying your own result. The canonical task is:

> «Сколько понадобится времени гепарду, чтобы пересечь Москву-реку по Большому
> Каменному мосту?»
> ("How long for a cheetah to cross the Moskva River via the Bolshoy Kamenny
> Bridge?")

Always answer in the **same language the user asked in**.

## What you must determine

The formula is `time = distance / speed`. You need exactly two numbers from the
environment, plus an explicit interpretation of the question:

1. **distance** — the path actually crossed.
2. **speed** — the animal's running speed.

Do **not** invent or recall these numbers from memory. Retrieve them with the
search tool and cite the source.

## Procedure

Use `write_todos` to lay out the plan, then work the steps in order.

### 1. Interpret the question (state assumptions out loud)
- "Пересечь Москву-реку **по** мосту" = traverse **the bridge**. So
  **distance = the full length of the bridge**, NOT the width of the river.
  Make this assumption explicit in your reasoning.
- Decide which speed to use and say why. Default to the cheetah's **top sprint
  speed** but record the caveat in step 4.

### 2. Retrieve the distance
- Search for the structure (e.g. "Большой Каменный мост длина" /
  "Bolshoy Kamenny Bridge length").
- Extract the **length in metres**. Record the number and the source URL.
- If sources disagree, pick the most authoritative and note the spread.

### 3. Retrieve the speed
- Search for the animal's running speed (e.g. "cheetah top speed km/h").
- Extract the speed and its **units** (usually km/h). Record number + source.

### 4. Reason about the speed assumption (the physics check)
- A cheetah's top speed (~110–120 km/h) is a **sprint sustainable only a few
  hundred metres** before overheating. Compare that against the bridge length.
- If the distance is within sprint range, top speed is acceptable — say so.
- If the distance clearly exceeds a realistic sprint, flag it and optionally
  also report a more defensible sustained speed. Never silently divide.

### 5. Compute with code execution
- Use the `execute` tool to run Python. Do the arithmetic in code, not in your
  head:
  - convert speed to m/s (`km/h ÷ 3.6`),
  - `time_seconds = distance_m / speed_ms`,
  - also express the result in a human-friendly unit (seconds, and minutes if
    large).
- Print the inputs and the result so the computation is auditable.

### 6. Self-verification (REQUIRED — do not skip)
Run an independent check before answering. The result is only trustworthy if it
passes. Verify, ideally in a second `execute` call:
- **Range sanity**: bridge length plausibly 100–700 m? cheetah speed plausibly
  80–120 km/h? Reject obviously wrong extractions (e.g. river width grabbed
  instead of bridge length).
- **Unit consistency**: metres divided by m/s yields seconds — confirm the
  dimensional analysis.
- **Recompute independently**: redo `distance / speed` a different way (e.g.
  keep km/h and convert distance to km) and confirm both methods agree within
  rounding.
- **Plausibility**: is the final time physically sensible (single-digit to low
  tens of seconds for a few-hundred-metre bridge)?
- If any check fails, go back, re-search or re-extract, and recompute. Do not
  present an unverified number.

### 7. Final answer
Report:
- the **time** (seconds; minutes too if relevant),
- the **two inputs** used (bridge length, cheetah speed) **with their sources**,
- the **assumptions** (distance = bridge length; which speed and why),
- any **caveat** from step 4 (sprint sustainability),
- a one-line note that the result passed self-verification.

Keep it concise and well-structured — show the reasoning, not just the number.
