import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        We can infer that the cells are mines only if the numbers of
        cells exactly match the count of the set, otherwise there's
        still uncertainty, and thus we return an empty set.
        """
        if len(self.cells) == self.count and self.count != 0:
            return set(self.cells)
        return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        Likewise, we can say that a group of cells is safe if we know
        that the count of mines for a specific set is 0
        """
        if self.count == 0:
            return set(self.cells)
        return set()



    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine, by removing the cell from
        the considered cells in the sentence and decreasing the count
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        self.safes.add(cell)
        # 3) add a new sentence to the AI's knowledge base
        #    based on the value of `cell` and `count`
        neighbors = self.get_neighbors(cell)
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)
        # 4) mark any additional cells as safe or as mines
        #    if it can be concluded based on the AI's knowledge base
        # 5) add any new sentences to the AI's knowledge base
        #    if they can be inferred from existing knowledge
        self.knowledge = self.evaluate_knowledge(new_sentence)


    def evaluate_knowledge(self, last_sentence):
        """
        Re-evaluates all the sentences checking if there are new_mines/safes,
        if the sentence can be remove and/or if there are new sentences
        that can be inferred, reiterating the loop until no_changes are made.
        """
        new_knowledge = self.knowledge[:]
        changes = 1
        while changes:
            changes = 0
            new_mines = set()
            new_safes = set()
            for sentence in new_knowledge:
                # Removes the sentence from the knowledge if there are no more cells
                if len(sentence.cells) == 0 or sentence.count < 0:
                    new_knowledge.remove(sentence)
                    changes += 1
                #Checks if the sentence can reveal mines
                if sentence.known_mines():
                    new_mines.update(sentence.known_mines())
                #Checks if the sentence can reveal safes
                if sentence.known_safes():
                    new_safes.update(sentence.known_safes())
                #Checks if a new sentence can be inferred
                inferred_sentence = self.relationship(sentence, last_sentence)
                if inferred_sentence:
                    new_knowledge.append(inferred_sentence)
                    changes += 1

            for new_mine in (new_mines - self.mines):
                self.mark_mine(new_mine)
                changes += 1

            for new_safe in (new_safes - self.safes):
                self.mark_safe(new_safe)
                changes += 1
        return new_knowledge


    def relationship(self, sent1, sent2):
        if sent1.cells.issubset(sent2.cells):
            subset = sent1.cells - sent2.cells
            sub_count = sent1.count - sent2.count
            return Sentence(subset, sub_count)

        if sent2.cells.issubset(sent1.cells):
            subset = sent2.cells - sent1.cells
            sub_count = sent2.count - sent1.count
            return Sentence(subset, sub_count)
        return None




    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0:
            return None
        safe_moves = self.safes - self.moves_made - self.mines
        return random.choice(list(safe_moves)) if len(safe_moves) > 0 else None

    def get_boundaries(self, index, upper_boundary):
        lower = max(0, index -1)
        higher = min(upper_boundary, index + 1)
        return range(lower, higher +1 )


    def get_neighbors(self, cell):
        x, y = cell
        neighbors = set()
        rows, cols = self.get_boundaries(x, self.width), self.get_boundaries(y, self.height)
        for neigh_cell in itertools.product(rows, cols):
            if neigh_cell != cell and neigh_cell not in self.moves_made:
                neighbors.add(neigh_cell)
        return neighbors



    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = []
        for row in range(self.width):
            for column in range(self.height):
                cell = row, column
                if cell not in self.mines and cell not in self.moves_made:
                    available_moves.append(cell)
        return random.choice(available_moves) if len(available_moves) > 0 else None

