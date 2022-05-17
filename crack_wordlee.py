import time
import random
import argparse
import collections

from wordlee import Wordlee


class Cracker():
    
    def __init__(self, length):
        self.length = length
        self.wl = Wordlee()
        self.wl._init_game(self.length)        
        self.word_list = [*filter(lambda x: len(x) == self.length, self.wl.word_list)]
        random.shuffle(self.word_list)
        self.letters = [l for w in self.word_list for l in w]
        self.distribution = collections.Counter(self.letters)
        self.distribution = self.distribution.most_common()
        self.banned_letters = []
        self.word = ("#" * self.length)
        self.possible_letters = []
        self.old_candidates = []
        self.attempts = []

    def _update_string(self, string, val, i):
        string_l = list(string)
        string_l[i] = val
        return "".join(string_l)

    def search(self, eval_result, guess):
        for i, r in enumerate(eval_result):
            guess_i = guess[i]
            if r == -1:
                self.banned_letters.append(guess_i)
            elif r == 0:
                self.possible_letters.append(guess_i)
            else:
                self.word = self._update_string(self.word, guess_i, i)    

    def filter_candidates(self, candidates):
        filtered_candidates = []
        for c in candidates:
            true_count = 0
            if c in self.attempts or not all(possible_leter in c for possible_leter in self.possible_letters):
                continue
            for i, letter in enumerate(c):
                if letter in self.banned_letters:
                    continue                
                if self.word[i] == letter or self.word[i] == "#":
                    true_count += 1
            if true_count == len(c):
                filtered_candidates.append(c) 
        return filtered_candidates


    def make_nth_guess(self):        
        if len(self.old_candidates) == 0:
            self.old_candidates = self.word_list.copy()

        candidates = self.filter_candidates(self.old_candidates)        

        candidates_letters = set(list("".join(candidates)))
        self.distribution = [*filter(lambda e: e[0] not in self.banned_letters and e[0] in candidates_letters, self.distribution)]        

        guess = [*filter(lambda x: self.distribution[0][0] in x, candidates)][0]        
        self.old_candidates = candidates
        self.attempts.append(guess)
        return guess

    def check_if_done(self, g_eval):
        if sum(g_eval) == len(g_eval):
            # print(f"> Done")
            # print(f"> {self.wl.round-1} rounds")
            return True
        return False

    def log_result(self, success):
        # time (use as id); correct_word; attempts; length; success 
        print(f"{time.time()};{self.wl.word};{self.attempts};{self.wl.round-1};{self.length};{success}")

    def crack(self):
        # print(f"# Crack {time.time()} #")
        # print(f"> Random Word: {self.wl.word}")
        try:
            first_guess = [*filter(lambda x: self.distribution[0][0] in x and self.distribution[1][0] in x, self.word_list)][0]
        except IndexError as e:            
            first_guess = self.word_list[0]            
        # first_guess = "stroke"
        # print("> Starting ...") # : " + first_guess)
        first_eval_res = self.wl.eval_guess(first_guess)
        self.attempts.append(first_guess)
        # self.wl.vis_guess(first_eval_res, first_guess)
        self.search(first_eval_res, first_guess)
        if self.check_if_done(first_eval_res):
            self.log_result(success = True)
            return 1

        for x in range(self.wl.max_tries):
            nth_guess = self.make_nth_guess()
            nth_eval_res = self.wl.eval_guess(nth_guess)            
            # self.wl.vis_guess(nth_eval_res, nth_guess)
            self.search(nth_eval_res, nth_guess)
            # print(f"> W: {self.word}")
            if self.check_if_done(nth_eval_res):
                self.log_result(success = True)
                return 1
        self.log_result(success = False)               



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", help="Wordle Word Length", type=int, default=5)   
    args = parser.parse_args()

    length = args.length
    cracker = Cracker(length)
    cracker.crack()
