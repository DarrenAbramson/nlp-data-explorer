# nlp-data-explorer
Repository for simple, portable explorers of popular NLP datasets.

This contains explorers for three datasets: one by itself, CommonSense QA, and an explorer to measure quality between
a handcrafted, researcher sourced data set (small): Winograd,  and a crowdsourced data set with similar 
structure (large): Winogrande.

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

3. Some people think that bigger is better when it comes to language models. We disagree! 

In fact, surveyable data sets, meta-curated by people, can help with all the usual GIGOs of crawling the entire web for making a biased human language model. NOTE: the idea that we could produce an "unbiased" language model has been known to be false since Quine's Two Dogmas, Kuhn's Scientific Revolutions, and even Bacon's Organum. 

If Bookscorpus and Wikipedia on `albert-xx-large-v2` using [PLLs](https://arxiv.org/abs/1910.14659) [can do this well on common sense; (early draft, please only cite in small caps)](http://darrenabramson.com/paper.pdf), then filtering noisy, [cascade-causing](https://dl.acm.org/doi/abs/10.1145/3411764.3445518) arm's-length, exploitative data sets such as CQA into the better and worse parts as we have done here is just the beginning for compact, high-quality language models. 

`albert-xxlarge-v2_CQA.csv` is the result of concatenating question with answers and selecting the one that is the most likely PLL for the model as correct. The corresponding explorer lets you mix and randomly select from questions albert got right and wrong, so as to reliably get as sense both of the model's ability and the quality of the data set. 

`subsetScores` is similar, applied to Winograd and Winogrande (but pickled instead of being written to csv). To do. This file allows you to use `A_Subset_Explorer.py` and `A_Subset_Complement_Explorer.py` to selectively look at questions from each that Albert got wrong (the former) , or questions from each that Albert got right (the latter).
