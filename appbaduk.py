import streamlit as st
import numpy as np
import random

# 바둑판 크기 선택 드롭다운 메뉴
board_size = st.selectbox('바둑판 크기를 선택하세요', options=[19, 13, 9, 7], index=2)  # 기본값은 9x9

# 바둑판 초기화
if 'board' not in st.session_state or st.session_state.board.shape[0] != board_size:
    st.session_state.board = np.zeros((board_size, board_size), dtype=int)
    st.session_state.move_count = 0  # 총 놓은 돌의 수

# 사용자 인터페이스 설정
st.title('Simple AI Baduk 덤벼라 김서진!')
st.write(f'플레이어는 흑(1)입니다. AI는 백(2)입니다. 바둑판 크기: {board_size}x{board_size}')

# 바둑판을 출력하는 함수
def display_board(board):
    st.write('### Board Status')
    board_display = board.astype(str)  # 배열을 문자열로 변환
    board_display[board == 1] = "●"  # 흑돌
    board_display[board == 2] = "○"  # 백돌
    board_display[board == 0] = " "  # 빈칸
    st.table(board_display)  # 표 형식으로 바둑판 표시

# 바둑판에 돌을 두는 함수
def place_stone(board, x, y, player):
    x -= 1  # 입력값을 0-based 인덱스로 변환
    y -= 1  # 입력값을 0-based 인덱스로 변환
    if board[x, y] == 0:
        board[x, y] = player
        capture_stones(board, x, y, player)
        st.session_state.move_count += 1  # 돌을 둘 때마다 수 증가
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
        if 0 <= nx < board_size and 0 <= ny < board_size and board[nx, ny] == opponent:
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
        if 0 <= nx < board_size and 0 <= ny < board_size:
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
            if 0 <= nx < board_size and 0 <= ny < board_size and board[nx, ny] == player:
                stack.append((nx, ny))

# 개선된 몬테카를로 트리 탐색 알고리즘을 사용한 AI
def mcts_ai_move(board):
    empty_positions = list(zip(*np.where(board == 0)))
    best_move = None
    best_score = float('-inf')

    # 모든 빈 자리를 시뮬레이션하여 가장 좋은 수를 선택
    for move in empty_positions:
        score = evaluate_position(board, move, player=2)
        if score > best_score:
            best_score = score
            best_move = move

    # 가장 좋은 수를 선택하여 둠
    if best_move:
        place_stone(board, best_move[0] + 1, best_move[1] + 1, 2)  # 0-based에서 1-based로 변환
        st.write(f'AI가 ({best_move[0] + 1}, {best_move[1] + 1}) 위치에 돌을 두었습니다.')
    else:
        st.write('더 이상 둘 수 있는 위치가 없습니다.')

# 새로운 평가 함수: 목적에 맞는 수를 선택하도록 함
def evaluate_position(board, move, player):
    board_copy = board.copy()
    place_stone(board_copy, move[0] + 1, move[1] + 1, player)  # 0-based에서 1-based로 변환

    # 중앙에 가까울수록 점수를 높임
    center_x, center_y = board.shape[0] // 2, board.shape[1] // 2
    distance_to_center = np.sqrt((move[0] - center_x) ** 2 + (move[1] - center_y) ** 2)
    score = max(0, board_size - distance_to_center)

    # AI 돌이 1, 2선을 피하도록 보정
    if move[0] in [0, 1, board_size - 2, board_size - 1] or move[1] in [0, 1, board_size - 2, board_size - 1]:
        score -= 10  # 1선과 2선은 불리한 위치로 간주하여 점수 감소

    # 상대방 돌을 잡는 경우 점수 추가
    captured = count_captured_stones(board_copy, player)
    score += captured * 5  # 돌을 잡을수록 높은 점수

    # 집의 수를 기반으로 점수를 계산
    territory_score = calculate_territory(board_copy, player)
    score += territory_score

    return score

# 잡힌 돌의 수를 계산하는 함수
def count_captured_stones(board, player):
    opponent = 3 - player
    captured_count = 0
    for x in range(board_size):
        for y in range(board_size):
            if board[x, y] == opponent and not has_liberty(board, x, y, opponent):
                captured_count += 1
    return captured_count

# 집의 수를 계산하는 함수
def calculate_territory(board, player):
    visited = set()
    player_territory = 0
    opponent = 3 - player

    for x in range(board_size):
        for y in range(board_size):
            if board[x, y] == 0 and (x, y) not in visited:
                territory, owner = bfs_check_territory(board, x, y, visited)
                if owner == player:
                    player_territory += territory

    return player_territory

# BFS를 사용하여 특정 영역의 집과 소유자를 판단하는 함수
def bfs_check_territory(board, x, y, visited):
    queue = [(x, y)]
    territory = 0
    owner = None
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        cx, cy = queue.pop(0)
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        territory += 1

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                if board[nx, ny] == 0 and (nx, ny) not in visited:
                    queue.append((nx, ny))
                elif owner is None:
                    owner = board[nx, ny]
                elif board[nx, ny] != 0 and board[nx, ny] != owner:
                    return territory, None

    return territory, owner

# 사용자 입력
col1, col2 = st.columns(2)
x = col1.number_input('y 세로 좌표 (1-' + str(board_size) + ')', min_value=1, max_value=board_size, step=1)
y = col2.number_input('x 가로 좌표 (1-' + str(board_size) + ')', min_value=1, max_value=board_size, step=1)

# 돌 두기 버튼
if st.button('돌 두기'):
    if place_stone(st.session_state.board, x, y, 1):
        mcts_ai_move(st.session_state.board)
    display_board(st.session_state.board)
else:
    display_board(st.session_state.board)

# 집 계산 버튼
if st.button('집 계산'):
    black_territory = calculate_territory(st.session_state.board, 1)
    white_territory = calculate_territory(st.session_state.board, 2)
    st.write(f'흑(●)의 집: {black_territory} 개')
    st.write(f'백(○)의 집: {white_territory} 개')

    # 50%가 넘은 이후에만 승리 조건 체크
    if st.session_state.move_count > (board_size * board_size) // 2:
        total_territory = black_territory + white_territory
        if total_territory > 0:
            black_percentage = (black_territory / total_territory) * 100
            white_percentage = (white_territory / total_territory) * 100

            if abs(black_percentage - white_percentage) >= 25:
                if black_percentage > white_percentage:
                    st.write('**흑(●) 승리!**')
                else:
                    st.write('**백(○) 승리!**')
