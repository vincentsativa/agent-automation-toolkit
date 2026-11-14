# Illustrative Code Anchors for dev.to Pieces

Two shapes cover nearly every outline. Both are illustrative, both get labeled in the sentence above the fence, and neither asserts a result. Copy and adapt; do not compose a new one from memory.

## Why a business piece needs one

dev.to's audience is individual contributors and hands-on builders. A post that only moves money around reads as a press release to them, even when every number is right. The artifact is what converts a market observation into something they can act on, and it costs ten lines.

## Shape 1: the mechanism block

Goes in the mechanism or request-path section. The point is that the threshold, not the model name, is the cost lever, so the snippet has to make one number obviously load bearing.

```python
# illustrative routing policy, not a vendor SDK
policy = load("routing.yaml")

def handle(req):
    p = decider.judge(req.text, "does this need the frontier model?")
    model = "frontier" if p > policy.escalate_at else "small"
    with trace.span("route", model=model, p=p):
        return call(model, req)
```

The paragraph after it must name `escalate_at` and say what moving it does. Without that sentence the block is decoration.

## Shape 2: the criteria block

Goes where the article discusses evaluation, quality criteria, or a monitoring agent. Markdown fences render as code on dev.to, so a config or criteria file is a legitimate block, not a cop out.

```markdown
# goal.md
## A session must
- check seat availability before quoting a fare
- carry dietary constraints into every delegation
- name the tool call behind every price it reports

## A session fails when
- the response succeeds with zero tool calls
- a constraint set on turn one is missing at turn ten
```

Label it "illustrative and not <publisher>'s copy" when a real file exists but is unpublished. Inventing the exact contents of a vendor's internal config and presenting it as theirs is a fabricated artifact, which is the one thing a snippet must never be.

## Verification before sending

Both blocks are code. Confirm each one parses or the article ships a syntax error:

```python
import ast, re
src = open("devto-post.md").read()
for i, block in enumerate(re.findall(r"```python\n(.*?)```", src, re.S)):
    ast.parse(block)
    print("block", i, "parses")
print("fences:", src.count("```"))
```

An odd fence count means a block never closed. Even count with a fused line means a patch ate a newline inside the block, which `ast.parse` catches on the python side.

## What a snippet must never do

- Claim a measured result. Structure only, never "this cut latency 40%."
- Present a vendor's unpublished file as their real content.
- Run past about ten lines. Longer scrolls badly on a phone and stops being scannable.
- Replace the numbers. A snippet earns trust for the analysis; it does not substitute for it.
