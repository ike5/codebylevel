# CodeByLevel Documentation Format Specification

_Last updated: August 2025_

## Overview

CodeByLevel organizes documentation based on three dimensions:

1. **Skill Level** – Who the doc is for  
2. **Depth** – How detailed it should be  
3. **Presentation Style** – How it's displayed (code, prose, combo)

Every documentation file includes **structured metadata**, followed by **content blocks** written in a Markdown-inspired format with extended syntax for code blocks and dynamic rendering.

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
tags: ["lists", "comprehension", "syntax"]
---



Level Breakdown (level)

The level field uses this pattern: X.Y.Z
	•	X — Developer Level
	•	A = Newbie
	•	B = Intermediate
	•	C = Professional
	•	D = Expert
	•	E = Specialist
	•	Y — Depth of Detail
	•	1 = Conceptual / overview
	•	2 = Includes relationships, prototypes, inheritance
	•	3 = Multi-layered technical depth
	•	4 = Full breakdown, including edge cases and internals
	•	Z — Style of Explanation
	•	0 = Paragraph explanation only
	•	1 = Code-only
	•	2 = Paragraph + code (standard)
	•	3 = Diagrammatic or interactive explanation (future)

⸻

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
