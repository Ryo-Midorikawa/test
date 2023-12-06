import tkinter as tk
from queue import Queue


class WindowCanvasManager:
    def __init__(self, bg_color="black"):
        # ルートウィンドウの作成
        self.root = tk.Tk()

        # ウィンドウのサイズを画面の解像度に合わせる
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.attributes("-fullscreen", True)

        # 円の中心
        self.window_center = (screen_width / 2, screen_height / 2)
        # 円の半径
        self.circle_radius = min(screen_width, screen_height) / 2 - 200

        # 円の左上と右下の座標
        self.upper_left = (
            self.window_center[0] - self.circle_radius,
            self.window_center[1] - self.circle_radius,
        )
        self.lower_right = (
            self.window_center[0] + self.circle_radius,
            self.window_center[1] + self.circle_radius,
        )
        
        # degree instance
        self.input_degree = 0
        
        # キャンバスの作成
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width + 10,
            height=screen_height + 10,
            bg=bg_color,
        )
        self.canvas.place(x=-5, y=-5)

        # 描写された図形とテキストのIDを保持
        self.drown_arc_id = None
        self.drown_text_id = None

    def create_arc(self, *args, **kwargs):
        self.drown_arc_id = self.canvas.create_arc(*args, **kwargs)
        return self.drown_arc_id

    def create_text(self, *args, **kwargs):
        self.drown_text_id = self.canvas.create_text(*args, **kwargs)
        return self.drown_text_id

    def update_arc_angle(self, obj_id, start_angle):
        # 指定されたIDの円弧の角度を更新する
        self.canvas.itemconfig(obj_id, start=start_angle)

    # def update_text_content(self, obj_id, new_text):
    #     # 指定されたIDのテキストオブジェクトの内容を新しいテキストで更新する
    #     self.canvas.itemconfig(obj_id, text=new_text)
    
    def update_text_content_and_position(self, obj_id, new_text, x, y):
        # 指定されたIDのテキストオブジェクトの内容を新しいテキストで更新する
        self.canvas.itemconfig(obj_id, text=new_text)
        self.canvas.coords(obj_id,x,y)


    def delete_object(self, obj_id):
        self.canvas.delete(obj_id)

    def draw_voice_angle_arc_and_text_forever(
        self, voice_angle_queue: Queue, transcribed_text_queue: Queue
    ):
        print(self.drown_arc_id)
        print(self.drown_text_id)
        
        # TODO Queueから何回かNoneを取得したら円弧とテキストを削除する
        # Queueから角度を取得(ノンブロッキング)
        input_degree: int = (
            voice_angle_queue.get_nowait()
            if not voice_angle_queue.empty()
            else None
        )

        


        # Queueからテキストを取得(ノンブロッキング)
        input_text: str = (
            transcribed_text_queue.get_nowait()
            if not transcribed_text_queue.empty()
            else None
        )
        print(f"input_degree: {input_degree}, input_text: {input_text}")

        # どちらもNoneの場合は再帰呼び出し
        if input_degree is None and input_text is None:
            self.root.after(
                34,
                self.draw_voice_angle_arc_and_text_forever,
                voice_angle_queue,
                transcribed_text_queue,
            )
            return

        if input_degree is not None:
            # 緑川
            # input_degreeに関してしきい値（360度の範囲で）を適当に設定して右，正面，左の3方向を分割
            # 4パターンのinput_degreeに対してそれぞれxy座標を設定
            self.input_degree = input_degree
        
                
            
        
        if (self.input_degree >= 0 and self.input_degree <= 45) or (self.input_degree > 315 and self.input_degree <= 360):
            x = self.window_center[0] + self.circle_radius
            y = self.window_center[1]
        elif self.input_degree > 45 and self.input_degree <= 135:
            x = self.window_center[0]
            y = self.window_center[1] - self.circle_radius - 100
        elif self.input_degree > 135 and self.input_degree <= 225:
            x = self.window_center[0] - self.circle_radius
            y = self.window_center[1]
        else:
            x = self.window_center[0]
            y = self.window_center[1] + self.circle_radius + 100
            
        if input_text is not None:
            # テキストが描画されていない場合は描画する
            if self.drown_text_id is None:
                self.create_text(
                    self.window_center[0],
                    self.window_center[1] + self.circle_radius + 100,
                    text="Hello, world!",
                    fill="red",
                    font=("Arial", 24),
                    anchor="center",
                )
            # 緑川
            # テキストと位置を同時に更新
            else:
                self.update_text_content_and_position(self.drown_text_id, input_text, x, y)
                # 緑川
                # 位置の更新も同時に行う

        self.root.after(
            34,
            self.draw_voice_angle_arc_and_text_forever,
            voice_angle_queue,
            transcribed_text_queue,
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    import random
    import threading
    from time import sleep

    def angle_producer(q: Queue):
        while True:
            # Generate a random number between 0 and 360
            random_number = random.randint(0, 360)
            print(random_number)
            # Put the number in the queue
            q.put(random_number)
            # Sleep for 1 second
            sleep(1)

    def transcribed_text_producer(q: Queue):
        while True:
            # Generate a random alphabet
            random_alphabet = chr(random.randint(97, 122))
            print(random_alphabet)
            # Put the alphabet in the queue
            q.put(random_alphabet)
            # Sleep for 1 second
            sleep(2)

    voice_angle_queue: Queue = Queue()
    angle_producer_thread = threading.Thread(
        target=angle_producer, args=(voice_angle_queue,)
    )
    angle_producer_thread.start()

    transcribed_text_queue: Queue = Queue()
    transcribed_text_producer_thread = threading.Thread(
        target=transcribed_text_producer, args=(transcribed_text_queue,)
    )
    transcribed_text_producer_thread.start()

    window_canvas = WindowCanvasManager()
    window_canvas.draw_voice_angle_arc_and_text_forever(
        voice_angle_queue, transcribed_text_queue
    )
    window_canvas.run()
