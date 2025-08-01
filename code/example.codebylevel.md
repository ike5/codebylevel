---
language: python
version: 3.12
title: DataFrame
access: private
license: contributor
level: B.2.1
---

# DataFrame

A tabular structure used in pandas to store labeled, column-oriented data.

## Parameters

- `data`: input data (array, dict, etc.)
- `columns`: list of column names
- `index`: row labels

## Example

```python
import pandas as pd

df = pd.DataFrame([[1, 2], [3, 4]], columns=["A", "B"])
print(df)