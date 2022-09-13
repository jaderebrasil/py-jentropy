==========
PyJEntropy
==========

**PyJEntropy** is a repository for exploring applications
of entropy in a variety of problems.

We currently only have a Wordle (and similar) guessing game solver.


Usage
=====

.. code-block:: python

    import jentropy.wordle as w

    # currently, the possible words are
    #   w.WORDLE_GAMES['en5-nytimes']
    #   w.WORDLE_GAMES['en5-wordlegames']
    #   w.WORDLE_GAMES['pt5-wordlegames']
    # the list of allowed guesses was found in the respective
    # sites of each game.

    wor = w.Wordle(wordle_game)
    s = wor.entropy_series_allowed()

    first_guess = s[0]
    # guess in the game, observe the resultant pattern

    wor.next_step(first_guess, resultant_pattern)
    s = wor.entropy_series()

    # we can check wor.words to see which words are still possible
    # if a there's more than one word there, we can proceed
    second_guess = s[0]
    # repeat the process

In the future, I'll build a CLI to make the usage easy.

