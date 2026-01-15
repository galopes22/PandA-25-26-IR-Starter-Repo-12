# Part 12 - Starter

This part builds on your Part 11 solution. There will be almost no instructions this time. You do not need
them anymore ☺️.

Your task is to add **normalization** and **stemming**, e.g., the Porter stemmer to the system. See the ToDos for a bit more detail.

## Run the app

``` bash
python -m part12.app
```

## What to implement (ToDos)

Your ToDos are in `part12/models.py`, but you may create new modules, classes, and functions and restructure the code as you see fit.

0. First, **copy/redo** your implementation from Part 11. Move your solution for the **four TODOs** to the `models.py` module.

1. **Add stemming**. Either include the Porter stemmer from the slides or add a package containing a stemmer that you can use.  
   Our goal is to search for normalized, stemmed tokens instead of using tokens obtained by splitting on whitespace. 
Implement the normalization logic once and reuse it (1) during index creation and (2) during querying.

   Make sure that although we normalize and stem tokens, the **original token is highlighted**. For example, if due to normalization and stemming `summer` and `summer's` have the same stem, then when searching for `summer`, all occurrences of both tokens are highlighted.
