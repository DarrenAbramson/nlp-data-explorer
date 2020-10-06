# nlp-data-explorer
Repository for simple, portable explorers of popular NLP datasets.

This contains explorers for three datasets: 1 by itself, and an explorer to measure quality between
a handcrafted, researcher sourced data set (small) and a crowdsourced data set with similar structure (large)..

1. The "CommonSense QA" dataset, paper and data available at https://www.tau-nlp.org/commonsenseqa

Usage Example:

```python
python CQA_Explorer.py
```


2. The "Winograd" dataset, a small handmade (and completely cited!) data set available at https://cs.nyu.edu/faculty/davise/papers/WinogradSchemas/WS.html and
a similarly structured dataset, called "Winogrande" (portmanteau!) available at https://github.com/allenai/winogrande 

Usage Example:

```python
python WinWin_Explorer.py
```
