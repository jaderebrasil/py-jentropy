from enum import Enum
import logging
import os
from typing import List, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd
import itertools

log = logging.getLogger(__name__)

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
)

WORDLE_STD_GAME = 'en5-nytimes'
WORDLE_GAMES = {
    'en5-nytimes': 'en5-nytimes.txt',
    'en5-wordlegames': 'en5-wordlegames.txt',
    'pt5-wordlegames': 'pt5-wordlegames.txt',
}


WORD_S: int = 5
PATNUM: int = 243


class WordleChrRes(Enum):
    MISS = "⬛"
    MISPLACED = "🟨"
    EXACT = "🟩"

    @staticmethod
    def from_int(part: int) -> str:
        p = list(itertools.repeat(WordleChrRes.MISS.value, 5))
        aux = 0
        for i in range(WORD_S):
            x = ((part % (3**(i+1))) - aux) / (3**i)
            aux = x * (3**i) + aux
            if x == 1:
                p[i] = WordleChrRes.MISPLACED.value
            elif x == 2:
                p[i] = WordleChrRes.EXACT.value

        return ''.join(p)


class Wordle:
    _patnum: int = 0
    __allowed_words: List[str] = []
    _words: List[str] = []
    _pmtrx: npt.NDArray[np.int_] | None = None
    _fallowed: str
    _fnpy: str

    def __init__(self, fallowed: str = WORDLE_GAMES[WORDLE_STD_GAME]):
        if os.path.exists(self.__data_fpath(fallowed)):
            self._fallowed = self.__data_fpath(fallowed)
            self._fnpy = self.__data_fpath(f'pattern_matrix_{fallowed}.npy')

        res = []
        with open(self._fallowed) as file:
            res.extend([word.strip() for word in file.readlines()])
        self.__allowed_words = sorted(res)
        self._words = self.__allowed_words.copy()

    @staticmethod
    def __data_fpath(fname: str) -> str:
        return os.path.join(DATA_DIR, fname)

    @property
    def pmtrx(self) -> npt.NDArray[np.int_]:
        if self._pmtrx is None:
            if os.path.exists(self._fnpy):
                self._pmtrx = np.load(self._fnpy)
            else:
                self._pmtrx = self.__generate_pmtrx()
                np.save(self._fnpy, self._pmtrx)

        return self._pmtrx

    def __generate_pmtrx(self) -> npt.NDArray[np.int_]:
        wslen = self.allowed_size
        mtrx = np.zeros((wslen, wslen + PATNUM), dtype=int)

        log.info('generating pmrtx: this may take a few minutes.')
        for i, j in itertools.product(range(wslen), range(wslen)):
            wpar = self.words[i]
            word = self.words[j]
            parn = self._partnum(wpar, word)
            mtrx[i][j] = parn
            mtrx[i][wslen + parn] += 1
        log.info('generating pmrtx: done!.')

        return(mtrx)

    @property
    def words(self) -> List[str]:
        '''
        Return the all words that can be the answer in the current
        step.
        '''
        return self._words

    @words.setter
    def words(self, value) -> None:
        self._words = value

    @property
    def allowed_words(self) -> List[str]:
        return self.__allowed_words

    @property
    def allowed_size(self) -> int:
        return len(self.__allowed_words)

    def next_step(self, guess: str, pattern: int) -> None:
        ind = self.allowed_words.index(guess)
        words_ind = np.array([self.allowed_words.index(w) for w in self.words])
        wline = self.pmtrx[ind, words_ind]
        wslen = len(words_ind)

        new_words_ind: List[int] = []
        for i in range(wslen):
            if wline[i] == pattern:
                new_words_ind.append(words_ind[i])

        self.words = [self.allowed_words[i] for i in new_words_ind]

    def entropy_series_allowed(self) -> Optional[pd.Series]:
        words_list = self.allowed_words.copy()
        wslen = len(words_list)
        words_ind = np.array([self.allowed_words.index(w) for w in words_list])
        r = PATNUM + wslen

        prob = self.pmtrx[:, self.allowed_size:r][words_ind] / wslen
        logp = np.log2(prob, where=prob > 0)

        entropy = -np.sum(prob * logp, axis=1)

        return pd.Series(entropy,
                         index=words_list).sort_values(ascending=False)

    def _partnum(self, wpar: str, word: str) -> int:
        res = 0
        try:
            for i in range(len(wpar)):
                if wpar[i] == word[i]:
                    res += 2 * (3 ** i)
                elif wpar[i] in word:
                    res += 1 * (3 ** i)
        except Exception as e:
            log.debug(f'{wpar}({len(word)}) - {word}({len(word)})')
            log.debug(f'\nException: {e}')
            exit(1)

        return res

    def entropy_series(
        self,
        words_list: Optional[List[str]] = None
    ) -> Optional[pd.Series]:
        if words_list is None:
            words_list = self.words

        wslen = len(words_list)
        alen = len(self.allowed_words)
        words_ind = np.array([self.allowed_words.index(w) for w in words_list])

        reducedmx = self.pmtrx[:, words_ind]
        prob = np.zeros((alen, PATNUM))

        for i in range(alen):
            row = reducedmx[i]
            uniq, count = np.unique(row, return_counts=True)
            prob[i, np.array(uniq).astype(int)] = count

        prob = prob / wslen
        logp = np.log2(prob, where=prob > 0)

        entropy = -np.sum(prob * logp, axis=1)

        return pd.Series(entropy,
                         index=self.allowed_words).sort_values(ascending=False)

    def entropy_word(self, wpar: str) -> float:
        wslen = len(self.words)
        wpari = self.allowed_words.index(wpar)

        part = np.zeros(PATNUM)
        for word in self.words:
            wordi = self.allowed_words.index(word)
            p = self.pmtrx[wpari, wordi]
            part[p] += 1

        prob = part / wslen
        logp = np.log2(prob, where=prob > 0)

        entropy = -np.sum(prob * logp).astype(float)

        return entropy

    def entropy_word_r(self, wpar: str) -> float:
        wslen = len(self.words)

        part = np.zeros(PATNUM)
        for j in range(wslen):
            word = self.words[j]
            p = self._partnum(wpar, word)
            part[p] += 1

        prob = part / wslen
        logp = np.log2(prob, where=prob > 0)

        entropy = -np.sum(prob * logp).astype(float)

        return entropy

    def words_in_part(self, wpar: str, part: int) -> List[str]:
        ipar = self.allowed_words.index(wpar)
        asize = self.allowed_size
        wrow = self.pmtrx[ipar][0:asize]

        words_ind = np.where(wrow == part)[0]

        return [self.allowed_words[i] for i in words_ind]
