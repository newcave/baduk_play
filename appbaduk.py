import streamlit as st
import numpy as np
import random

# 바둑판 초기화 (19x19)
if 'board' not in st.session_state:
    st.session_state.board = np.zeros((19, 19), dtype=int)

# 사용자 인터페이스 설정
st.title('간단한 바둑 게임 (19x19)')
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
        return True
    else:
        st.write('해당 위치에 이미 돌이 있습니다. 다른 위치를 선택하세요.')
        return False

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
    current_player = 3 - player  # 교대

    # 무작위로 돌을 두면서 게임 진행
    while True:
        empty_positions = list(zip(*np.where(board_copy == 0)))
        if not empty_positions:
            break
        random_move = random.choice(empty_positions)
        place_stone(board_copy, random_move[0], random_move[1], current_player)
        current_player = 3 - current_player  # 교대

    # 임의로 백의 승률을 높이기 위한 방식 (단순한 버전)
    return np.sum(board_copy == 2)

# 사용자 입력
col1, col2 = st.columns(2)
x = col1.number_input('x 좌표 (0-18)', min_value=0, max_value=18, step=1)
y = col2.number_input('y 좌표 (0-18)', min_value=0, max_value=18, step=1)

# 돌 두기 버튼
if st.button('돌 두기'):
    if place_stone(st.session_state.board, x, y, 1):
        mcts_ai_move(st.session_state.board)
    display_board(st.session_state.board)
else:
    display_board(st.session_state.board)
