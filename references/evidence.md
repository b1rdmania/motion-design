# Evidence ledger

`plan/evidence.json` lists every claim the film makes: in words, in numbers, and in images that imply a fact. `check.py` gates on it. A wrong number in 60-point type is the worst mistake this format makes, and the agent that animates the number cannot tell that it is wrong.

## Format

```json
{
  "claims": [
    {
      "id": "wait-time",
      "type": "fact",
      "source": "https://example.com/survey-2026",
      "evidence": "Median wait for a puncture repair across 40 London shops: 7 days (table 2).",
      "permitted_wording": "seven days for a puncture.",
      "limits": "London shops in the survey only; not a national figure.",
      "beats": ["b1"]
    },
    {
      "id": "clock-rewind",
      "type": "metaphor",
      "source": "editorial device",
      "evidence": "A wall clock running backwards stands for time given back to the rider.",
      "permitted_wording": null,
      "limits": "Must not imply a guaranteed same-day repair.",
      "beats": ["b4"]
    }
  ]
}
```

In the score, a beat names the claims it uses: `"proves": "wait-time"`, or a list of ids.

## Types

| Type | Means | Needs |
|---|---|---|
| `fact` | Checkable and true | `source` and `evidence`. This can be a URL and an excerpt, a dataset and a query, a calculation, or a product behaviour you demonstrated. |
| `inference` | Reasoned from facts but not itself checkable | `evidence` saying what it is inferred from, and `limits` |
| `metaphor` | A visual or verbal device | `limits`, saying what it must not be taken to mean |

## What check.py does with it

- A `fact` with no source or evidence fails. This is blocking.
- A beat whose `proves` names an unknown id fails. This is blocking.
- Any on-screen text or VO line that contains a digit or a percent sign must name a claim, or it fails. This is blocking.
- A line with a number word ("seven", "twice", "half") and no claim becomes `needs_review`. It might be a quantity claim or just a phrase like "one place".
- A beat that uses a `metaphor` claim becomes `needs_review`. Check that the image and words do not present it as a fact.
- On-screen wording that differs from `permitted_wording` becomes `needs_review`.

## Rules

- Do not put private data on screen (addresses, names, contacts, owners) just to make a shot feel real.
- If data is public, do not imply that it is exclusive.
- Illustrative geometry, mock UI and sample data get their own claims, with limits saying so.
