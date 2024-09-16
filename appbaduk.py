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

# 간단한 AI (무작위로 수를 둠)
def ai_move(board):
    empty_positions = list(zip(*np.where(board == 0)))
    if empty_positions:
        move = random.choice(empty_positions)
        place_stone(board, move[0], move[1], 2)
        st.write(f'AI가 ({move[0]}, {move[1]}) 위치에 돌을 두었습니다.')
    else:
        st.write('더 이상 둘 수 있는 위치가 없습니다.')

# 사용자 입력
col1, col2 = st.columns(2)
x = col1.number_input('x 좌표 (0-18)', min_value=0, max_value=18, step=1)
y = col2.number_input('y 좌표 (0-18)', min_value=0, max_value=18, step=1)

# 돌 두기 버튼
if st.button('돌 두기'):
    if place_stone(st.session_state.board, x, y, 1):
        ai_move(st.session_state.board)
    display_board(st.session_state.board)
else:
    display_board(st.session_state.board)
