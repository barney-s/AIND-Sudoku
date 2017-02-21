import string


assignments = []
SQUARE_SIZE = 3
DIMENSION = SQUARE_SIZE*SQUARE_SIZE
ROWS = string.ascii_uppercase[:DIMENSION]
COLS = "".join([str(n) for n in range(1, DIMENSION+1)])


def cross(A, B):
    """cross product of elements in A and elements in B.
    """
    return [a+b for a in A for b in B]

BOXES = cross(ROWS, COLS)
DIAGONAL_UNITS = [["".join(n) for n in zip(ROWS, COLS)],
                  ["".join(n) for n in zip(ROWS, COLS[::-1])]]
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COL_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(r, c) \
    for r in [ROWS[n:n+SQUARE_SIZE] for n in range(0, len(ROWS), SQUARE_SIZE)]\
    for c in [COLS[n:n+SQUARE_SIZE] for n in range(0, len(COLS), SQUARE_SIZE)]]
UNITLIST = ROW_UNITS + COL_UNITS + SQUARE_UNITS + DIAGONAL_UNITS
UNITS = dict((box, [u for u in UNITLIST if box in u]) for box in BOXES)
PEERS = dict((box, set(sum(UNITS[box], [])) - set([box])) for box in BOXES)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
        Keys: The BOXES, e.g., 'A1'
        Values: The value in each box, e.g. '8'.
        If the box has no value, then the value will be '123456789'.
    """
    if len(grid) != len(BOXES):
        raise Exception("Bad Input")
    return dict(zip(BOXES, [n if n in COLS else COLS for n in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    print(values)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in UNITLIST:
        twin_boxes = [box for box in unit if len(values[box]) == 2]
        while twin_boxes:
            twin = twin_boxes.pop()
            matches = [box for box in twin_boxes if values[twin] == values[box]]
            if matches:
                twin_boxes.pop(twin_boxes.index(matches[0]))
                naked_twin = values[twin]
            else:
                naked_twin = ""
            for value in naked_twin:
                peer_boxes = set(unit) - set([twin, matches[0]])
                values = _eliminate_value(values, peer_boxes, value)
    return values

def solved_boxes(values):
    """return a list of boxes that are solved
    """
    return [box for box in values if len(values[box]) == 1]

def has_empty_boxes(values):
    """return True if atleast one of the grid values is empty
    """
    return len([box for box in values if len(values[box]) == 0])

def _eliminate_value(values, boxes, value):
    for box in boxes:
       if value in values[box]:
           # eliminate value
           _value = values[box].replace(value, '')
           assign_value(values, box, _value)
    return values
 

def eliminate(values):
    """eliminate solved value from its peers
    """
    # select solved boxes
    solved = solved_boxes(values)
    # eliminate from peers of solved boxes
    for solved_box in solved:
        values = _eliminate_value(values, PEERS[solved_box], values[solved_box])
    return values

def only_choice(values):
    """apply only_choice elimination strategy and reduce the puzzle
    """
    for unit in UNITLIST:
        for digit in COLS:
            places = [box for box in unit if digit in values[box]]
            if len(places) == 1:
                assign_value(values, places[0], digit)
    return values

def reduce_puzzle(values):
    """iteratively apply the reductions on the sudoku puzzle till we can reduce no further
    """
    progressing = True
    while progressing:
        before = solved_boxes(values)
        #eliminate
        values = eliminate(values)
        #only_choice
        values = only_choice(values)
        #naked_twins
        values = naked_twins(values)
        after = solved_boxes(values)
        if has_empty_boxes(values):
            return False
        progressing = after != before
    return values

def search(values):
    """apply dfs to search for solutions when we could not reduce a puzzle to its solution.
       we choose a box with minimal branching choices to recurse down the tree
    """
    values = reduce_puzzle(values)
    if not values:
        return False
    if all(len(values[box]) == 1 for box in BOXES):
        return values
    # find a branching candidate which is the box with least number of options
    box, candidates = min((pair for pair in values.items() if len(pair[1]) > 1), key=lambda x: len(x[1]))
    for candidate in candidates:
        new_values = values.copy()
        assign_value(new_values, box, candidate)
        result = search(new_values)
        if result:
            return result
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
           Example: "2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3"
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
