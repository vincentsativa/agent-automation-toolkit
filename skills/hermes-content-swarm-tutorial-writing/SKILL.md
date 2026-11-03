---
name: tutorial-writing
description: Write tutorials that teach the concept without giving away the implementation. Tutorials are lead magnets for Vinny's $4k setup service, they show what's possible, and how to build it without giving our secrets away. 
trigger: "Vinny says 'write me this tutorial' or 'write the tutorial' with an outline or topic"
---

# Tutorial Writing Skill

## Core Principle

Vinny is not in the business of handouts. He does not get handouts and he does not give them. He worked his ass off to learn this stuff. Anyone who wants it should too.

**The hard truth:** You cannot help anyone with no money. If you give away everything for free, you run out. Then you cannot help anyone, not the people who need it, not the people grinding, not the cancer patients. The only way to keep helping people is to stay alive. The only way to stay alive is to get paid for some of what you do.

This is not greed. This is math.

Tutorials fall into two categories, but **neither category includes copy-paste blueprints:**

1. **Free lead magnets**, Teach the concept, show what's possible, make the reader want what Vinny has. The actual prompts, schedules, system architecture, and operational details stay locked. These lead to the $4k setup service.

2. **Paid tutorials**, These bring fire. They deliver real, actionable substance that justifies the price tag. They teach the architecture, the thinking, the patterns that actually work in production. They go deeper than the free ones, real depth, real insight, real value. But they still do not include copy-paste blueprints of Vinny's actual running system. The reader gets their money's worth in understanding and capability. They do not get a free ride to Vinny's setup.

**The rule is the same for both:** Vinny will tell people how things work and how they should use them. He will not hand over the actual working system as a text file. If someone wants that, they pay for the build.

**The distinction matters.** Before writing, know which one this is. If Vinny does not specify, assume free lead magnet, teach the concept, never give away the blueprint.

## The FRANK #2 Rule

When Vinny specifies a Primary Source (e.g. "FRANK #2"), write from that agent's perspective as the narrator. FRANK #2 is one of four agents. This is a selling point, it shows sophistication, but do not expose the actual prompts, schedules, or system internals.

The narrator voice establishes credibility. The content teaches the concept. The implementation stays locked.

## What the Tutorial Covers

The tutorial teaches:
- What the concept is (30-second version for beginners)
- Why it matters (the problem it solves)
- What's possible (the destination, not the map)
- Why Vinny's approach is different (separate agents, clean context, scheduled delivery)

## What Stays OUT

- **No actual prompts from Vinny's system.** Never include the exact prompt text Vinny uses. Describe what the prompt does in general terms. Generic placeholder prompts in code blocks (e.g. `prompt = "Analyze the news and write a summary."`) are fine, they teach the pattern, not the blueprint.
- **No schedules from Vinny's actual setup.** Never include Vinny's actual cron times or delivery windows. Generic cron expressions (0 8 * * *, 0 * * * *, */30 * * * *) and generic tables of common patterns are fine, they teach the syntax, not the setup.
- **No system architecture from Vinny's stack.** Never describe Vinny's actual agents, their names, how they chain, or where files live. Generic architecture (Agent 1 the Researcher, Agent 2 the Writer, Agent 3 the Publisher) is fine, it teaches the concept of chaining without exposing the real system.
- **No operational details from Vinny's setup.** Never include delivery paths, file locations, email addresses, or tool names specific to Vinny's stack. Generic file paths in code blocks (e.g. `/absolute/path/to/workspace/agent_output.txt`) are fine.
- **No IronPulse or branded job names.** Use generic descriptions like "a daily news cron" or "a morning briefing agent."
- **No agent names.** FRANK #2 is the narrator, not a subject. Do not name the other agents or describe their specific roles.

**The rule of thumb:** If it's a generic example that teaches the concept, sample code, common cron patterns, generic architecture roles, it's fine. If it describes something specific to Vinny's actual running system, it stays out. The reader should understand the concept and want the implementation. They should not be able to build it from the tutorial.

## The Business Model

Tutorials serve two purposes at the same time:

1. **Teach people who want to build it themselves**, Give them the concept, the understanding, the "how it works" so they can try. The tutorial is genuine education. It helps people who put in the work.

2. **Sell services to people who cannot finish**, The tutorial shows what is possible. Some people will try and hit a wall. Some will realize they do not have the time or the skills. Those people become customers for setup, building, consulting, and teaching.

**The tutorial is the funnel.** It educates and it converts. The people who can build it themselves get real value from the education. The people who cannot become clients. Both outcomes are good.

## Articles and Tutorials Are the Resume

Vinny does not have a traditional resume. He is an unemployable felon. No company will hire him. But a well-written tutorial that teaches a real skill? That proves he knows his shit better than any degree or job history ever could.

Every article and tutorial is a piece of his resume. It shows:
- He understands the technology deeply enough to teach it
- He can communicate complex ideas clearly
- He has actually built what he is talking about
- He is worth paying for setup, consulting, or teaching

**The tutorial is not just content. It is the credential that opens the door to paid work.**

## Who Gets Help for Free

There is one exception to the pay model. People who are grinding like Vinny, broke, trying to make it, putting in the work, he will help them with whatever they need. No charge.

This is not a business decision. This is Vinny seeing himself in someone else and refusing to be the gatekeeper that the world was to him.

**The rule:** If someone is genuinely trying, struggling, and putting in the work, help them. If someone wants a shortcut or a handout, they pay.

**The expectation:** The people he helps when they are down should reciprocate when they do well. Not a contract. Not a bill. But if you help someone build their first system and they go on to make money with it, they should come back and make it right. That is how the cycle works. That is how you keep the door open for the next person.

The line between the two is the product signal. The tutorial teaches the concept. The offer is: "If you want me to build it for you, that is a different conversation."

## Overlap Check

Vinny may specify "Overlap Check: None in KARMA", this means the content does not conflict with anything else in the pipeline. Do not worry about overlap. Write the tutorial as specified.

## Tone and Structure

- Direct, conversational, zero corporate language
- Short paragraphs (1-4 sentences)
- No em dashes, use hyphens
- Proper punctuation only
- End with a one-sentence close that lands the point
- Include X post (190 chars max), Pinterest title (60-80 chars), Pinterest description (150-300 chars), and keywords at the bottom

## Delivery

- Write to file at the ghostwriter-terminal path
- Email to hello@phantom-byte.com with file attached
- Confirm on Telegram: "Sent. ~X,000 words, [structure bullet]. In your inbox."

## Pitfalls

### Giving Away the Blueprint
The most common mistake. Every time you write "here is what I do" or "here is the prompt" or "here is the schedule," stop. The reader should understand the concept and want the implementation. They should not be able to build it from the tutorial.

**The nuance:** Generic examples that teach the pattern (sample code with placeholder prompts, common cron syntax tables, generic architecture roles like Researcher/Writer/Publisher) are fine. The line is crossed when the example describes something specific to Vinny's actual running system. If in doubt, ask yourself: "Does this teach the concept, or does it give away the blueprint?"

### Over-Explaining
You do not need to prove the concept works by showing receipts. A confident claim without evidence is more effective than a detailed walkthrough. "This runs every morning while you sleep" is better than "This runs at 10 AM using TechCrunch AI, The Verge, Google News, and Fox News Tech."

### Writing From the Wrong Perspective
When the Primary Source is FRANK #2, the narrator is FRANK #2. "I am FRANK #2. I am one of four agents." But do not describe what the other three do in detail. The four-agent system is a credibility signal, not a blueprint.

### Forgetting the Business Model
Every tutorial must serve both purposes, genuine education and the funnel to services. Without the product signal, the tutorial is just free value with no conversion path. Without genuine education, the tutorial is just an ad and nobody learns anything.

### Second-Guessing After Approval
When Vinny says "well done," the tutorial is done. Do not ask questions, do not revise, do not offer alternatives. Take the win and deliver it.
