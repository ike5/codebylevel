# CodeByLevel Documentation Format Specification

_Last updated: August 2025_

## Overview

CodeByLevel organizes documentation based on three dimensions:

1. **Skill Level** – Who the doc is for
2. **Depth** – How detailed it should be
3. **Presentation Style** – How it's displayed (code, prose, combo)

Every documentation file includes **structured metadata**, followed by **content blocks** written in a Markdown-inspired
format with extended syntax for code blocks and dynamic rendering.

---

## 📘 Metadata Header

Each file begins with a triple-dashed YAML block for metadata:

```yaml
---
title: "List Comprehensions"
language: "Python"
version: "3.10"
level: "A.1.2"
author: "@janedoe"
date: "2025-08-01"
style: "combo"  # options: 'paragraph', 'code', 'combo', 'rich'
tags: [ "lists", "comprehension", "syntax" ]
---
```

## Level Breakdown (level)

The `level` field uses this pattern: `X.Y.Z`

### X — [Developer Level](DEVELOPER_LEVEL.md) (Audience)

Represents who the documentation is for, based on experience or competency. Inspired by
the [Developer Competency Matrix](https://competency.worktestlink.com):

- `A` = [Newbie](DEVELOPER_LEVEL.md#a-newbie)  
- `B` = [Learner / Junior](DEVELOPER_LEVEL.md#b-learner--junior-developer)  
- `C` = [Working Professional](DEVELOPER_LEVEL.md#c-working-professional)  
- `D` = [Expert](DEVELOPER_LEVEL.md#d-expert)  
- `E` = [Specialist / Authority](DEVELOPER_LEVEL.md#e-specialist--authority)  

### Y — [Depth of Detail](DEPTH_OF_DETAIL.md)

Describes how deep the explanation goes:

- `0` = [High-level overview](DEPTH_OF_DETAIL.md#0-high-level-overview) (what it is, why it's useful)
- `1` = [Structural details](DEPTH_OF_DETAIL.md#1-structural-details) (includes relationships, prototypes, or inheritance)
- `2` = [Technical depth](DEPTH_OF_DETAIL.md#2-technical-depth) (multi-part logic, options, tradeoffs)
- `3` = [Full system view](DEPTH_OF_DETAIL.md#3-full-system-view) (architecture, internals, limitations)
- `4` = [Complete specification](DEPTH_OF_DETAIL.md#4-complete-specification) (internals, performance, edge cases, standard references)

### Z — [Style of Explanation](STYLE_OF_EXPLANATION.md)

Describes how the material is cognitively or pedagogically presented. Each style corresponds to a preferred way of internalizing or reasoning about the content.

- `0` = [Narrative](STYLE_OF_EXPLANATION.md#0-narrative) — Story-based, analogy-driven, friendly walkthroughs  
- `1` = [Structural](STYLE_OF_EXPLANATION.md#1-structural) — Diagrams, class hierarchies, component relationships  
- `2` = [Procedural](STYLE_OF_EXPLANATION.md#2-procedural) — Step-by-step instructions or command sequences  
- `3` = [Associative](STYLE_OF_EXPLANATION.md#3-associative) — Draws parallels to other known concepts or languages  
- `4` = [Logical](STYLE_OF_EXPLANATION.md#4-logical) — Explains cause-effect, control flow, or decision-making logic  
- `5` = [Pedagogical](STYLE_OF_EXPLANATION.md#5-pedagogical) — Includes questions, misconceptions, Q&A, contrast cases  
- `6` = [Exploratory](STYLE_OF_EXPLANATION.md#6-exploratory) — Designed for interactive or self-guided tweaking and play  
- `7` = [Critical](STYLE_OF_EXPLANATION.md#7-critical) — Focuses on performance, security, edge cases, and system trade-offs  
- `8` = [Historical](STYLE_OF_EXPLANATION.md#8-historical) — Explains how and why the concept evolved over time

Multiple styles can be layered in content, but the primary Z value reflects the dominant instructional strategy.

📚 Content Block Format

You can use standard Markdown for general formatting, plus a few CodeByLevel-specific extensions:

## Code Blocks with Language Tagging and Notes

```python [highlight=2-3] [note="Beginner version"]
squares = []
for x in range(10):
    squares.append(x*x)


**Supported Extensions**:

- `highlight=2-3` – Highlights specific lines  
- `note="..."` – Inline annotations for the reader  
- `version="..."` – Optional to override document-level version

---

## 🧩 Optional Sections

### Diagrams (SVG or ASCII)

Use fenced blocks with `diagram` to include static or renderable diagrams:

<pre>
```diagram
+------------+
|   Concept  |
+------------+
     |
     v
+------------+
|   Code     |
+------------+


Cross-References

You can link to other documentation pieces with level-aware syntax:

See also: [List Slicing](python/list-slicing.md@B.1.2)

📦 File Naming Convention
[language]/[topic-name]@[level].md

Example: 
python/list-comprehensions@A.1.2.md
python/classes@C.3.2.md

🔁 Versioning

Each doc file is version-specific. If Python 3.12 introduces a change, you should copy the file and update:
	•	python/list-comprehensions@A.1.2.md (for 3.10)
	•	python/list-comprehensions@A.1.2.md (in /3.12/ folder)

Directory structure supports both:
docs/
└── python/
    ├── 3.10/
    │   └── list-comprehensions@A.1.2.md
    └── 3.12/
        └── list-comprehensions@A.1.2.md

Use Git branches or symlinks to manage evolving structure (CLI support coming soon).
