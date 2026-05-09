# ─────────────────────────────────────────────
#  ai/minimax.py  –  Minimax + Alpha-Beta Pruning
# ─────────────────────────────────────────────
# """
# Used exclusively by the Boss Tank.

# MAX player = Boss Tank   → maximises evaluation heuristic
# MIN player = Human       → minimises Boss's heuristic

# The game state passed in is a lightweight dict so we avoid
# mutating the real game objects during the search.
# """

ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'SHOOT']

# Heuristic weights (from project spec)
W_CLOSE_PROXIMITY  =  60   # player within 3 tiles
W_LINE_OF_SIGHT    =  50   # can shoot immediately
W_COVER            =  30   # boss adjacent to steel
W_PLAYER_HP_MISS   =  20   # per missing player HP
W_BOSS_HP_MISS     = -40   # per missing boss HP (penalty)
W_PLAYER_FOREST    = -20   # player hidden in forest


# ── Performance counters (reset each decision) ────────────────
stats = {'nodes_no_pruning': 0, 'nodes_with_pruning': 0}


def reset_stats():
    stats['nodes_no_pruning'] = 0
    stats['nodes_with_pruning'] = 0


# ── Heuristic ─────────────────────────────────────────────────

def evaluate(state):
    # Evaluate a game state from the Boss's perspective.
    # state keys: bx, by, px, py, boss_hp, player_hp, grid, steel_positions
    bx, by = state['bx'], state['by']
    px, py = state['px'], state['py']
    score = 0

    # Proximity
    dist = abs(bx - px) + abs(by - py)
    if dist <= 3:
        score += W_CLOSE_PROXIMITY

    # Line of sight (same row or column, no wall between)
    if bx == px:
        blocked = any(
            state['grid'].get(bx, y) in (1, 2, 3)   # BRICK, STEEL, WATER
            for y in range(min(by, py) + 1, max(by, py))
        )
        if not blocked:
            score += W_LINE_OF_SIGHT
    if by == py:
        blocked = any(
            state['grid'].get(x, by) in (1, 2, 3)
            for x in range(min(bx, px) + 1, max(bx, px))
        )
        if not blocked:
            score += W_LINE_OF_SIGHT

    # Cover: boss adjacent to a steel tile
    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        if state['grid'].get(bx + dx, by + dy) == 2:   # STEEL
            score += W_COVER
            break

    # HP factors
    score += W_PLAYER_HP_MISS * (3 - state.get('player_hp', 3))
    score += W_BOSS_HP_MISS   * (10 - state.get('boss_hp', 10))

    # Player hidden in forest
    if state['grid'].get(px, py) == 4:   # FOREST
        score += W_PLAYER_FOREST

    return score


# ── State simulation helpers ───────────────────────────────────

def _apply_action(state, action, is_boss):
    # Return a NEW state after applying action. Does not mutate input.
    s = dict(state)
    if is_boss:
        x, y = s['bx'], s['by']
        nx, ny = _move(x, y, action, s['grid'])
        s['bx'], s['by'] = nx, ny
    else:
        x, y = s['px'], s['py']
        nx, ny = _move(x, y, action, s['grid'])
        s['px'], s['py'] = nx, ny
    return s


def _move(x, y, action, grid):
    deltas = {'UP': (0,-1), 'DOWN': (0,1), 'LEFT': (-1,0), 'RIGHT': (1,0), 'SHOOT': (0,0)}
    dx, dy = deltas[action]
    nx, ny = x + dx, y + dy
    if grid.is_passable(nx, ny):
        return nx, ny
    return x, y


# ── Minimax ───────────────────────────────────────────────────

def minimax(state, depth, alpha, beta, is_max_turn, use_pruning=True):
    # Returns (best_score, best_action).
    # is_max_turn=True  -> Boss's turn (MAX - tries to get high score)
    # is_max_turn=False -> Player's simulated turn (MIN - tries to lower Boss's score)
    stats['nodes_with_pruning'] += 1

    # BASE CASE: Stop recursion when depth is 0
    if depth == 0:
        return evaluate(state), None

    best_action = None

    if is_max_turn:
        best_score = float('-inf')
        for action in ACTIONS:
            child = _apply_action(state, action, is_boss=True)
            score, _ = minimax(child, depth - 1, alpha, beta, False, use_pruning)
            if score > best_score:
                best_score, best_action = score, action
            if use_pruning:
                # PRUNING: If this score is already better than what MIN can allow, 
                # we stop exploring this branch (Beta Cut-off)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break   
        return best_score, best_action

    else:
        best_score = float('inf')
        for action in ACTIONS:
            child = _apply_action(state, action, is_boss=False)
            score, _ = minimax(child, depth - 1, alpha, beta, True, use_pruning)
            if score < best_score:
                best_score, best_action = score, action
            if use_pruning:
                # PRUNING: If this score is lower than what MAX expects, 
                # MAX won't pick this path anyway (Alpha Cut-off)
                beta = min(beta, score)
                if alpha >= beta:
                    break   
        return best_score, best_action


def minimax_no_pruning(state, depth):
    # Same search without pruning — used to count extra nodes for the report.
    stats['nodes_no_pruning'] += 1
    if depth == 0:
        return evaluate(state), None
    best_action = None
    best_score = float('-inf')
    for action in ACTIONS:
        child = _apply_action(state, action, is_boss=True)
        score, _ = _min_node(child, depth - 1)
        if score > best_score:
            best_score, best_action = score, action
    return best_score, best_action


def _min_node(state, depth):
    stats['nodes_no_pruning'] += 1
    if depth == 0:
        return evaluate(state), None
    best_score = float('inf')
    best_action = None
    for action in ACTIONS:
        child = _apply_action(state, action, is_boss=False)
        score, _ = _max_node(child, depth - 1)
        if score < best_score:
            best_score, best_action = score, action
    return best_score, best_action


def _max_node(state, depth):
    stats['nodes_no_pruning'] += 1
    if depth == 0:
        return evaluate(state), None
    best_score = float('-inf')
    best_action = None
    for action in ACTIONS:
        child = _apply_action(state, action, is_boss=True)
        score, _ = _min_node(child, depth - 1)
        if score > best_score:
            best_score, best_action = score, action
    return best_score, best_action


def get_boss_action(state, depth):
    # Main entry point for the Boss Tank each tick.
    # Returns (best_action, pruning_stats_dict).
    reset_stats()

    # Run WITH pruning (used in actual game)
    _, action = minimax(state, depth, float('-inf'), float('inf'), True, use_pruning=True)
    pruned_nodes = stats['nodes_with_pruning']

    # Run WITHOUT pruning (just for measurement / report)
    reset_stats()
    minimax_no_pruning(state, depth)
    full_nodes = stats['nodes_no_pruning']

    report = {
        'depth': depth,
        'nodes_with_pruning': pruned_nodes,
        'nodes_without_pruning': full_nodes,
        'speedup': round(full_nodes / max(pruned_nodes, 1), 2),
    }

    return action or 'SHOOT', report
