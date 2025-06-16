from pygame import *
import chess
import sys

# Initialize Pygame and constants
init()
WIDTH, HEIGHT = 512, 512
SQUARE_SIZE = WIDTH // 8
FPS = 60

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)

# Load images (assumes images named like wp.png, bN.png, etc.)
IMAGES = {}
def load_images():
    pieces = ['p', 'n', 'b', 'r', 'q', 'k']
    colors = ['w', 'b']
    for color in colors:
        for piece in pieces:
            filename = f"{color}{piece.upper()}.png"
            IMAGES[color + piece] = transform.scale(image.load(filename), (SQUARE_SIZE, SQUARE_SIZE))
load_images()

# Chess engine logic
transposition_table = {}

piece_values = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
}

def evaluate_board(board):
    if board.is_checkmate():
        return float('-inf') if board.turn == chess.WHITE else float('inf')
    elif board.is_stalemate() or board.is_insufficient_material():
        return 0
    score = 0
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            val = piece_values[p.piece_type]
            score += val if p.color == chess.WHITE else -val
    return score

def order_moves(board):
    def score_move(move):
        score = 0
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            victim_val = piece_values.get(victim.piece_type, 0) if victim else 0
            attacker_val = piece_values.get(attacker.piece_type, 0) if attacker else 0
            score += 10 * victim_val - attacker_val
        if move.promotion:
            score += 8
        if board.gives_check(move):
            score += 5
        return score
    return sorted(board.legal_moves, key=score_move, reverse=True)

def minimax(board, depth, alpha, beta, maximizing_player):
    key = (board.fen(), depth, maximizing_player)
    if key in transposition_table:
        return transposition_table[key]
    if depth == 0 or board.is_game_over():
        val = evaluate_board(board)
        transposition_table[key] = val
        return val
    if maximizing_player:
        max_eval = float('-inf')
        for move in order_moves(board):
            board.push(move)
            val = minimax(board, depth-1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        transposition_table[key] = max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in order_moves(board):
            board.push(move)
            val = minimax(board, depth-1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        transposition_table[key] = min_eval
        return min_eval

def find_best_move(board, depth):
    best_move = None
    best_val = float('inf')  # AI is black (minimizing)
    alpha = float('-inf')
    beta = float('inf')
    for move in order_moves(board):
        board.push(move)
        val = minimax(board, depth-1, alpha, beta, True)
        board.pop()
        if val < best_val:
            best_val = val
            best_move = move
            beta = min(beta, val)
    return best_move

# Draw functions
def draw_board(screen):
    colors = [LIGHT, DARK]
    for r in range(8):
        for c in range(8):
            color = colors[(r+c) % 2]
            draw.rect(screen, color, Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            color = 'w' if piece.color == chess.WHITE else 'b'
            key = color + piece.symbol().lower()
            screen.blit(IMAGES[key], (col*SQUARE_SIZE, row*SQUARE_SIZE))

# Main
def main():
    screen = display.set_mode((WIDTH, HEIGHT))
    display.set_caption("Chess with AI (Black)")
    clock = time.Clock()

    board = chess.Board()
    selected_square = None
    running = True
    thinking = False

    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == MOUSEBUTTONDOWN and not thinking:
                x, y = e.pos
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                sq = chess.square(col, 7 - row)

                if selected_square is None:
                    # Select piece to move (only white)
                    p = board.piece_at(sq)
                    if p and p.color == chess.WHITE:
                        selected_square = sq
                else:
                    # Attempt move
                    move = chess.Move(selected_square, sq)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None

                        # Check game over after player move
                        if board.is_game_over():
                            print("Game Over:", board.result())
                            running = False
                            break

                        # AI turn
                        thinking = True
                    else:
                        # Deselect if invalid
                        selected_square = None

        if thinking:
            best_move = find_best_move(board, depth=5)
            if best_move:
                board.push(best_move)
                print(f"AI plays: {best_move}")
            else:
                print("AI has no legal moves.")
            thinking = False

            if board.is_game_over():
                print("Game Over:", board.result())
                running = False

        draw_board(screen)
        draw_pieces(screen, board)

        # Highlight selected square
        if selected_square is not None:
            row = 7 - (selected_square // 8)
            col = selected_square % 8
            draw.rect(screen, HIGHLIGHT, Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

        display.flip()
        clock.tick(FPS)

    quit()
    sys.exit()

if __name__ == '__main__':
    main()
