# Google's "Bridge Theory to Code" Recommendation, Known-Good Guardrail Block

**Verified working Aug 2026 (Article 148).** Google repeatedly tells PhantomByte that conceptual security/architecture articles read as thought-leadership and should become bookmarkable engineering resources by injecting a short, practical code block. The fix is a `// THE GUARDRAIL IN CODE`-style section with a working example of the concept the article only described verbally.

## The reusable template

Adapt the tool names, paths, and banned markers per article. This exact block satisfied the Google recommendation for the AI-agent security article.

````
// THE GUARDRAIL IN CODE

Here is what enforcement looks like, not described, but running. Google's environment hooks let you register a function that runs before every tool call. It checks the call against a deterministic policy and denies it before the model ever executes it.

```python
# pre_tool_call hook: intercept before the model executes
def pre_tool_call(context):
    call = context.get("tool_call", {})
    name = call.get("name", "")
    if name != "code_execution":
        return {"status": "allow"}
    payload = call.get("input", "")
    banned = ["rm -rf", "os.system", "subprocess", "eval("]
    if any(marker in payload for marker in banned):
        return {
            "status": "deny",
            "reason": "blocked by deterministic policy, not model judgment",
        }
    return {"status": "allow"}
```

Register that hook against the Managed Agent and code_execution calls carrying those markers are refused by the runtime. The model does not get asked. There is no prompt to jailbreak. The policy lives outside the model, so the worm cannot reason its way around it.

The same shape applies to SteerPlane. The tool is declarative. You write the rule, it enforces it in code.

```yaml
guardrails:
  - path: "/tmp/work/**"
    deny:
      - write_file
      - delete_file
  - path: "/home/user/**"
    deny:
      - code_execution
```

The agent never sees the rule. It only meets the consequence. That is the difference between a suggestion and a boundary.
````

## Why this satisfies the recommendation

- **Concrete, executable**, not "consider a guardrail" but a callable function and a declarative config.
- **Ties the article's abstract thesis (defense lives outside the model) to a runnable artifact**, exactly what Google means by "bookmarkable engineering resource."
- **Uses the exact tools the article names** (Gemini hooks, SteerPlane) so the section reinforces, not contradicts, the surrounding prose.
- **Zero em dashes** in the block itself, write it that way from the start.
