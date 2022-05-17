import random	

# from colorama import init
from colorama import Fore, Back, Style
 
# init()

class Wordlee:
	def __init__(self):
		self.word_file = "english-nouns.txt"
		self.load_words()
		
	def _init_game(self, difficulty):
		self.difficulty = difficulty
		self.word = self.get_random_word()
		# self.word = "cousin" 
		self.word_len = len(self.word)
		self.len_output = (f"Length: {self.word_len}")
		start_output = (self.word_len* "*")
		self.max_tries = 6
		self.tries = 6
		self.round = 1
		self.past_outputs = [self.len_output, start_output]

	def get_random_word(self):
		random.shuffle(self.word_list)
		return [*filter(lambda x: len(x) == self.difficulty, self.word_list)][0]
		
	def load_words(self):
		with open(self.word_file) as f:
			content = f.read()
			self.word_list = content.split("\n")
	
	def eval_guess(self, guess):
		"""
		0 = correct char
		1 = correct char & correct pos
		-1 = False
		"""
		eval_results = []
		for gi, g in enumerate(guess):
			tmp_eval_value = -1
			for wi, w in enumerate(self.word):			
				if g in w and gi == wi:
					tmp_eval_value = 1
				if tmp_eval_value < 0 and g in w:
					tmp_eval_value = 0
			eval_results.append(tmp_eval_value)	
		
		self.tries -= 1
		self.round += 1
		return eval_results
		
	def _style(self, eval_res, element):
		if eval_res == 0:
			return Fore.BLACK + Style.BRIGHT + Back.YELLOW + element + Style.RESET_ALL
		elif eval_res == 1:
			return Fore.BLACK + Style.BRIGHT + Back.GREEN + element + Style.RESET_ALL
		else:
			return Fore.WHITE + Style.BRIGHT + element + Style.RESET_ALL
			
		
	def vis_guess(self, guess_eval_results, guess_input):
		string_output = ""
		for geres_i, geres in enumerate(guess_eval_results):
			string_output += self._style(geres, guess_input[geres_i])
		self.past_outputs.append(string_output)		
		print(string_output)
	
	def play(self, diff):
		self._init_game(diff)
		while self.tries > 0:
			print(50*"-")
			print(f"Round #{self.round}")
			for outputs_ in self.past_outputs:
				print(outputs_)
			guess_input = input("")
			eval_res = self.eval_guess(guess_input)
			self.vis_guess(eval_res, guess_input)			
		print("####################")
		print("Correct Word: ")
		print(self.word)


# wl = Wordlee()
# wl.play(3)

