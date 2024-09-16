import streamlit as st
import numpy as np
import random

# 바둑판 초기화 (9x9)
if 'board' not in st.session_state:
    st.session_state.board = np.zeros((9, 9), dtype=int)

# 사용자 인터페이스 설정
st.title('간단한 바둑 게임 (9x9)')
st.write('플레이어는 흑(1)입니다. AI는 백(2)입니다.')

# 바둑판을 출력하는 함수
def display_board(board):
    st.write('### 바둑판 상태')
    board_display = board.astype(str)  # 배열을 문자열로 변환
    board_display[board == 1] = "●"  # 흑돌
    board_display[board == 2] = "○"  # 백돌
    board_display[board == 0] = " "  # 빈칸
    st.table(board_display)  # 표 형식으로 바둑판 표시

# 바둑판에 돌을 두는 함수
def place_stone(board, x, y, player):
    if board[x, y] == 0:
        board[x, y] = player
        capture_stones(board, x, y, player)
        return True
    else:
        st.write('해당 위치에 이미 돌이 있습니다. 다른 위치를 선택하세요.')
        return False

# 상대방의 돌을 잡는 함수
def capture_stones(board, x, y, player):
    opponent = 3 - player
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 9 and 0 <= ny < 9 and board[nx, ny] == opponent:
            if not has_liberty(board, nx, ny, opponent):
                remove_group(board, nx, ny, opponent)

# 돌 그룹에 자유가 있는지 확인하는 함수
def has_liberty(board, x, y, player):
    visited = set()
    return check_liberty(board, x, y, player, visited)

def check_liberty(board, x, y, player, visited):
    if (x, y) in visited:
        return False
    visited.add((x, y))
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 9 and 0 <= ny < 9:
            if board[nx, ny] == 0:  # 자유점이 있으면 True 반환
                return True
            if board[nx, ny] == player and check_liberty(board, nx, ny, player, visited):
                return True
    return False

# 상대방의 돌 그룹을 제거하는 함수
def remove_group(board, x, y, player):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        board[cx, cy] = 0  # 돌을 제거
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 9 and 0 <= ny < 9 and board[nx, ny] == player:
                stack.append((nx, ny))

# 몬테카를로 트리 탐색 알고리즘을 사용한 간단한 AI
def mcts_ai_move(board):
    empty_positions = list(zip(*np.where(board == 0)))
    best_move = None
    best_score = -1

    # 모든 빈 자리를 시뮬레이션하여 승률이 가장 높은 수를 선택
    for move in empty_positions:
        score = simulate_random_playout(board, move, player=2)
        if score > best_score:
            best_score = score
            best_move = move

    # 가장 좋은 수를 선택하여 둠
    if best_move:
        place_stone(board, best_move[0], best_move[1], 2)
        st.write(f'AI가 ({best_move[0]}, {best_move[1]}) 위치에 돌을 두었습니다.')
    else:
        st.write('더 이상 둘 수 있는 위치가 없습니다.')

# 무작위 시뮬레이션을 통해 각 수의 승률을 계산
def simulate_random_playout(board, move, player):
    board_copy = board.copy()
    place_stone(board_copy, move[0], move[1], player)

    # 중앙에서 멀어질수록 점수가 낮아짐 (중앙 집중형 전략)
    center_x, center_y = board.shape[0] // 2, board.shape[1] // 2
    distance_to_center = np.sqrt((move[0] - center_x) ** 2 + (move[1] - center_y) ** 2)
    score = max(0, 9 - distance_to_center)  # 중앙에 가까울수록 높은 점수

    # AI 돌이 1, 2선을 피하도록 보정
    if move[0] in [0, 1, 7, 8] or move[1] in [0, 1, 7, 8]:
        score -= 10  # 1선과 2선은 불리한 위치로 간주하여 점수 감소

    # 시뮬레이션 반복하여 점수 보정 (단순한 버전)
    current_player = 3 - player  # 교대
    while True:
        empty_positions = list(zip(*np.where(board_copy == 0)))
        if not empty_positions:
            break
        random_move = random.choice(empty_positions)
        place_stone(board_copy, random_move[0], random_move[1], current_player)
        current_player = 3 - current_player  # 교대

    return score

# 사용자 입력
col1, col2 = st.columns(2)
x = col1.number_input('x 좌표 (0-8)', min_value=0, max_value=8, step=1)
y = col2.number_input('y 좌표 (0-8)', min_value=0, max_value=8, step=1)

# 돌 두기 버튼
if st.button('돌 두기'):
    if place_stone(st.session_state.board, x, y, 1):
        mcts_ai_move(st.session_state.board)
    display_board(st.session_state.board)
else:
    display_board(st.session_state.board)
