function enterGuess(guess) {
    guess.toLowerCase().split('').forEach(c => {
        const button = document.querySelector(`button[data-key="${c}"]`);
        if (button) button.click();
        else console.error(`Button for letter "${c}" not found.`);
    });
    const enterButton = document.querySelector(`button[data-key="↵"]`);
    if (enterButton) enterButton.click();
    else console.error("Enter button not found.");
}

function getEvaluation() {
    const rows = Array.from(document.querySelectorAll(".Row-module_row__pwpBq"));
    return rows.map(row => {
        const tiles = Array.from(row.querySelectorAll(".Tile-module_tile__UWEHN"));
        return tiles.map(tile => ({
            letter: tile.innerText.trim(),
            state: tile.getAttribute("data-state")
        }));
    });
}

class WordleSolver {
    constructor(wordList, length) {
        this.wordList = wordList.filter(w => w.length === length);

        this.correctLetters = Array(length).fill(null); 
        this.presentLetters = new Map(); 
        this.absentLetters = new Set(); 

        // track letter counts across all feedback
        // minCount[char] = how many times char must appear in the solution
        // maxCount[char] = how many times char can appear at most
        this.minCount = {};
        this.maxCount = {};

        this.guesses = [];
        this.usedGuesses = new Set();
        this.lastGuess = null;

        // initialize maxCount for all letters to a large number
        for (let c = 97; c <= 122; c++) {
            const letter = String.fromCharCode(c);
            this.minCount[letter] = 0;
            this.maxCount[letter] = 5; // max 5 in a 5-letter word
        }
    }

    updateConstraints(guess, feedback) {
        // track how many times each letter was guessed this turn
        const guessLetterCount = {};
        guess.split("").forEach(char => {
            guessLetterCount[char] = (guessLetterCount[char] || 0) + 1;
        });

        // pass 1: process green (correct) first
        for (let i = 0; i < guess.length; i++) {
            const state = feedback[i];
            const char = guess[i];
            if (state === "correct") {
                // fix letter in position
                this.correctLetters[i] = char;

                // we know at least one of 'char' is used up here
                this.minCount[char] = Math.max(this.minCount[char], 1);
                // decrement local count
                guessLetterCount[char]--;
            }
        }

        // pass 2: handle yellow (present) and absent
        for (let i = 0; i < guess.length; i++) {
            const state = feedback[i];
            const char = guess[i];

            if (state === "present") {
                // must appear, but not in this position
                if (!this.presentLetters.has(char)) {
                    this.presentLetters.set(char, new Set());
                }
                this.presentLetters.get(char).add(i);

                // ensure we have enough of char
                this.minCount[char] = Math.max(this.minCount[char], 1);
                guessLetterCount[char]--;
            } else if (state === "absent") {
                // only ban if we have no leftover usage for it
                // or if char never appeared as green/present
                // if guessLetterCount[char] > 0, means we accounted for a green/present usage
                // so this particular instance is "excess" and thus absent
                if (!this.correctLetters.includes(char) && ![...this.presentLetters.keys()].includes(char)) {
                    // globally ban if no prior usage
                    this.maxCount[char] = 0;
                    this.absentLetters.add(char);
                } else if (guessLetterCount[char] > 0) {
                    // we've used up the min count for this letter, so reduce max
                    // for example, if minCount[char] is 1, but we guessed it twice,
                    // and the second time is absent => clamp maxCount
                    this.maxCount[char] = Math.min(this.maxCount[char], this.minCount[char]);
                    guessLetterCount[char]--;
                }
            }
        }
    }

    filterCandidates() {
        return this.wordList.filter(word => {
            // 1) check green letters
            for (let i = 0; i < this.correctLetters.length; i++) {
                const needed = this.correctLetters[i];
                if (needed && word[i] !== needed) return false;
            }
            // 2) check present letters not in their specific banned positions
            for (const [letter, invalidPositions] of this.presentLetters.entries()) {
                if (!word.includes(letter)) return false;
                for (const pos of invalidPositions) {
                    if (word[pos] === letter) return false;
                }
            }
            // 3) check absent letters
            //    must not appear unless it's forced green/present somewhere
            for (const letter of this.absentLetters) {
                // if it appears at all in the candidate without a known green
                // we fail
                if (word.includes(letter) && !this.correctLetters.some((l, i) => l === letter && word[i] === letter)) {
                    return false;
                }
            }
            // 4) enforce letter min/max counts
            const candidateCount = {};
            for (const c of word) {
                candidateCount[c] = (candidateCount[c] || 0) + 1;
            }
            // check each letter's min and max
            for (let c = 97; c <= 122; c++) {
                const letter = String.fromCharCode(c);
                const count = candidateCount[letter] || 0;
                if (count < this.minCount[letter]) return false;
                if (count > this.maxCount[letter]) return false;
            }

            return true;
        });
    }

    makeGuess() {
        const candidates = this.filterCandidates();
        if (candidates.length === 0) {
            console.error("No valid candidates remaining!");
            return null;
        }
        // avoid repeats
        for (const c of candidates) {
            if (!this.usedGuesses.has(c)) {
                this.usedGuesses.add(c);
                return c;
            }
        }
        // fallback if all are used (should rarely happen)
        return candidates[0];
    }

    async solve() {
        for (let attempt = 0; attempt < 6; attempt++) {
            const guess = this.makeGuess();
            this.lastGuess = guess;
            if (!guess) {
                console.error("Solver failed: No valid guesses left.");
                return;
            }

            console.log(`Attempt ${attempt + 1}: ${guess}`);
            enterGuess(guess);

            // wait for feedback to appear
            await new Promise(resolve => setTimeout(resolve, 2500));

            const allEvaluations = getEvaluation();
            const feedback = allEvaluations[attempt].map(tile => tile.state);

            console.log(`Feedback: ${feedback}`);

            // check if solved
            if (feedback.every(s => s === "correct")) {
                console.log(`Solved in ${attempt + 1} attempts! Word: ${guess}`);
                return;
            }

            this.updateConstraints(guess, feedback);
            this.guesses.push({ guess, feedback });
        }
        console.log("Solver failed: Could not solve within 6 attempts.");
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "solveWordle") {
        fetch(chrome.runtime.getURL("wordlist.txt"))
            .then(response => response.text())
            .then(text => {
                console.log("Word list loaded.");
                const wordList = text.split("\n").map(w => w.trim());
                const solver = new WordleSolver(wordList, 5);
                solver.solve();
            });
    }
});
