import numpy as np
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window

MARKS = {0: 'X', 1: 'O'}

class Board:
    def __init__(self):
        self.state = [None] * 9  # 9つのセルの状態（None = 空）
        self.counter = 0  # ターンカウント

    def render(self):
        # 現在のボードの状態をコンソールに出力
        text = """
        0 1 2
        3 4 5
        6 7 8
        """
        for idx, x in enumerate(self.state):
            if x is not None:
                text = text.replace(str(idx), MARKS[x])
        print(text)

    def move(self, idx):
        if self.state[idx] is not None:
            return False
        player = self.counter % 2
        self.state[idx] = player
        self.counter += 1
        return True

    def unmove(self, idx):
        self.counter -= 1
        self.state[idx] = None

    def is_win(self, player):
        s = self.state
        if (s[0] == s[1] == s[2] == player or
            s[3] == s[4] == s[5] == player or
            s[6] == s[7] == s[8] == player or
            s[0] == s[3] == s[6] == player or
            s[1] == s[4] == s[7] == player or
            s[2] == s[5] == s[8] == player or
            s[0] == s[4] == s[8] == player or
            s[2] == s[4] == s[6] == player):
            return True
        return False

    def is_end(self):
        return None not in self.state  # 空のセルがない場合、ゲーム終了

    def valid_moves(self):
        return [idx for idx, player in enumerate(self.state) if player is None]

# minimaxアルゴリズムをAIに追加
def minimax(board, player):
    maximize_player = 0
    minimize_player = 1

    if board.is_win(maximize_player):
        return 1, None
    elif board.is_win(minimize_player):
        return -1, None
    elif board.is_end():
        return 0, None

    opp = 1 if player == 0 else 0

    if player == maximize_player:
        max_score = -np.inf
        max_idx = None

        for idx in board.valid_moves():
            board.move(idx)
            score, _ = minimax(board, opp)
            if max_score < score:
                max_score = score
                max_idx = idx
            board.unmove(idx)

        return max_score, max_idx

    else:
        min_score = np.inf
        min_idx = None

        for idx in board.valid_moves():
            board.move(idx)
            score, _ = minimax(board, opp)
            if min_score > score:
                min_score = score
                min_idx = idx
            board.unmove(idx)

        return min_score, min_idx

class TicTacToeApp(App):
    def build(self):
        self.board = Board()  # ゲームボードのインスタンス
        self.current_player = 0  # 最初のプレイヤーは'X' (0)
        self.time_limit = 2  # 各ターンの制限時間（秒）

        self.turn_timer = self.time_limit
        self.timer_label = Label(text=f"Time Left: {self.turn_timer}s", font_size=20, size_hint_y=None, height=50)

        self.grid = GridLayout(cols=3, rows=3)  # 3x3のグリッド
        self.buttons = []

        for i in range(9):
            button = Button(
                text='', 
                font_size=40, 
                background_color=(0.5, 0.7, 0.9, 1), 
                on_press=self.on_button_press
            )
            button.index = i  # 各ボタンにインデックスを設定
            self.buttons.append(button)
            self.grid.add_widget(button)

        # プレイヤー情報ラベル
        self.status_label = Label(text="Player X's Turn", font_size=20, size_hint_y=None, height=50)

        # 勝敗記録の表示
        self.stats_label = Label(text="X Wins: 0 | O Wins: 0 | Draws: 0", font_size=16, size_hint_y=None, height=30)
        self.win_percentage_label = Label(text="X Win %: 0% | O Win %: 0%", font_size=16, size_hint_y=None, height=30)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.stats_label)
        layout.add_widget(self.win_percentage_label)
        layout.add_widget(self.timer_label)
        layout.add_widget(self.status_label)
        layout.add_widget(self.grid)

        # 勝敗記録
        self.x_wins = 0
        self.o_wins = 0
        self.draws = 0
        self.total_games = 0

        # タイマーの更新をスケジュール
        Clock.schedule_interval(self.update_timer, 1)

        return layout

    def update_timer(self, dt):
        if self.turn_timer > 0:
            self.turn_timer -= 1
            self.timer_label.text = f"Time Left: {self.turn_timer}s"
        else:
            # タイムオーバーで次のターンに切り替える
            self.switch_turn()

    def on_button_press(self, button):
        idx = button.index
        if self.board.move(idx):  # 成功したら
            button.text = MARKS[self.current_player]

            # 勝利判定
            if self.board.is_win(self.current_player):
                self.show_winner_popup(self.current_player)
            elif self.board.is_end():
                self.show_draw_popup()
            else:
                # プレイヤー交代
                self.switch_turn()

    def switch_turn(self):
        # 現在のターンが終了した後、ターンを切り替え
        if self.current_player == 0:
            self.current_player = 1
            self.status_label.text = f"Player O's Turn"
        else:
            self.current_player = 0
            self.status_label.text = f"Player X's Turn"

        self.turn_timer = self.time_limit  # タイマーをリセット
        self.timer_label.text = f"Time Left: {self.turn_timer}s"

        # タイムオーバーでAIターンが必要な場合に処理
        if self.current_player == 1:
            Clock.schedule_once(self.ai_turn, 1)  # 少し待ってからAIターンを開始

    def ai_turn(self, dt):
        score, idx = minimax(self.board, self.current_player)  # AIが最適な手を選択
        self.board.move(idx)
        self.buttons[idx].text = MARKS[self.current_player]

        # 勝利判定
        if self.board.is_win(self.current_player):
            self.show_winner_popup(self.current_player)
        elif self.board.is_end():
            self.show_draw_popup()
        else:
            self.switch_turn()

    def show_winner_popup(self, winner):
        # 勝者の判定と表示メッセージ
        winner_mark = MARKS[winner]
        if winner == 0:
            winner_message = "Player X wins!"
        else:
            winner_message = "Computer wins!"  # コンピュータの勝利

        popup = Popup(title='Game Over', content=Label(text=winner_message),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

        self.total_games += 1
        if winner == 0:
            self.x_wins += 1
        else:
            self.o_wins += 1

        self.update_stats()
        self.reset_game()

    def show_draw_popup(self):
        popup = Popup(title='Game Over', content=Label(text="It's a draw!"),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

        self.total_games += 1
        self.draws += 1
        self.update_stats()
        self.reset_game()

    def update_stats(self):
        self.stats_label.text = f"X Wins: {self.x_wins} | O Wins: {self.o_wins} | Draws: {self.draws}"
        # 勝率を計算して表示
        if self.total_games > 0:
            x_win_percent = (self.x_wins / self.total_games) * 100
            o_win_percent = (self.o_wins / self.total_games) * 100
        else:
            x_win_percent = o_win_percent = 0

        self.win_percentage_label.text = f"X Win %: {x_win_percent:.2f}% | O Win %: {o_win_percent:.2f}%"

    def reset_game(self):
        self.board = Board()  # ボードをリセット
        for button in self.buttons:
            button.text = ''
        self.current_player = 0
        self.status_label.text = "Player X's Turn"
        self.turn_timer = self.time_limit
        self.timer_label.text = f"Time Left: {self.turn_timer}s"

if __name__ == '__main__':
    TicTacToeApp().run()
