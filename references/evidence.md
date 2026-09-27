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
| `sample` | Sample data, mock UI, illustrative geometry or a demo screen | `limits`, saying what it is not (for example "sample data, not a forecast") |

## What the checks establish

- Facts missing source/evidence and references to unknown claim IDs are ledger errors.
- Numbers without IDs trigger review, not automatic failure: a product version or chapter label is not necessarily a factual performance claim.
- Nonnumeric and implied visual claims need review too. Every beat gets a coverage finding against the actual render.
- Populated fact/inference records get a source-support review. Verify the source, permitted scope and rendered wording; a nonempty field is not proof.
- Metaphors, sample data and changed wording get review prompts (`evidence.metaphor_wording`, `evidence.sample_labelled`, `evidence.permitted_wording`). Inferences need actual reasoning and limits; do not relabel an unsupported fact merely to bypass a gate.

Preserve private-source boundaries. Public data is not automatically exclusive. Label illustrative geometry, mock UI or sample data when their presentation would otherwise imply a real result. A film without factual claims can have an empty ledger, but that conclusion comes from inspecting its content, not a digit regex.
