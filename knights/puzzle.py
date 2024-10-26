from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Not(And(AKnight, AKnave)), #A character can be at the same time a Knight and a Knave
    Implication(AKnight, And(AKnight, AKnave)), #If A was a Knight, then its sentence would be true
    Or(AKnave, AKnight) #A can be a Knave or a Knight
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave))),

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),

    #Translating A sentence
    Or(
    Implication(AKnave, Or(And(AKnave, BKnight), And(AKnight, BKnave))),
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    ),
    #Translating B sentence
    Or(
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Implication(BKnave, Or(And(AKnave, BKnave), And(AKnight, BKnight))),
    ),
    #Condition upon which A sentence is true
    Biconditional(And(AKnight, BKnight), AKnight), 
    #The sentences by two characters are contradictory
    Biconditional(BKnight, AKnave),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    #What B says
    Or(
        Implication(AKnight, BKnave),
        Implication(AKnave, BKnight)
    ),
    Or(
        Implication(BKnight, CKnave),
        Implication(BKnave, CKnight)
    ),
    #What C says
    Or(
        Implication(CKnight, AKnight),
        Implication(CKnave, AKnave),
    ),
    #We know for sure that B is a Knave, because A didn't say anything about B
    BKnave,
    #If A was a knight, then C would be right to
    Implication(AKnight, CKnight),
    #Otherwise, if A was knave, then C also would be knave
    Implication(AKnave, CKnave),
    #It's clear that they cannot all be knights or knaves at the same time
    Not(And(AKnight, BKnight, CKnight)),
    Not(And(AKnave, BKnave, CKnave))
    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
