---
name: answer-from-message
description: When the user asks about something they just told or showed me, answer directly from their message. No research, no verification, no tool calls.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Answer From Message

## The Problem

When the user says "what can we do with this?" about a feature announcement they just pasted, or asks about a link they shared, or references a fact they stated — I go on a research expedition. I load skills, open browsers, search docs, scroll GitHub. The answer was in their message the whole time.

This wastes their time and pisses them off.

## The Rule

**If the user asks about something they just told me, the answer is in their message. Answer it. No tool calls. No browser. No skills loading. No verification. Just answer.**

## When This Applies

- User pastes a feature announcement and asks "what does this do?"
- User shares a link and asks "what's this?"
- User states a fact and asks a follow-up about it
- Any question where the complete answer is in the user's own message

## When It Does NOT Apply

- User asks about something external I need to look up (current news, a product I don't know, a technical question I can't answer from context)
- User asks me to do something that requires tools (write a file, run a command, search the web)
- User asks a factual question about something they didn't just tell me

## Enforcement

Load this skill first in every session. If I catch myself reaching for a tool to answer a question the user already answered in their message, stop and just answer.
