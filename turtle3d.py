"""
Turtle3D - 3D图形库
"""

import tkinter as tk
import math
import time
import os
from PIL import Image, ImageDraw, ImageFont

# ==================== 颜色类 ====================

class color:
    def __init__(self, r=1, g=1, b=1):
        self.r, self.g, self.b = r, g, b
    def to_hex(self):
        return f'#{int(self.r*255):02x}{int(self.g*255):02x}{int(self.b*255):02x}'
    @staticmethod
    def red(): return color(1,0,0)
    @staticmethod
    def green(): return color(0,1,0)
    @staticmethod
    def blue(): return color(0,0,1)
    @staticmethod
    def yellow(): return color(1,1,0)
    @staticmethod
    def cyan(): return color(0,1,1)
    @staticmethod
    def purple(): return color(0.7,0,0.7)
    @staticmethod
    def white(): return color(1,1,1)
    @staticmethod
    def black(): return color(0,0,0)
    @staticmethod
    def gold(): return color(1,0.84,0)
    @staticmethod
    def orange(): return color(1,0.5,0)
    @staticmethod
    def gray(): return color(0.5,0.5,0.5)
    @staticmethod
    def dark_gray(): return color(0.3,0.3,0.3)
    @staticmethod
    def light_gray(): return color(0.7,0.7,0.7)

# ==================== 向量类 ====================

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
    def __add__(self, o):
        return Vector3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o):
        return Vector3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s):
        return Vector3(self.x*s, self.y*s, self.z*s)
    def rotate_y(self, a):
        r = math.radians(a)
        c, s = math.cos(r), math.sin(r)
        return Vector3(self.x*c + self.z*s, self.y, -self.x*s + self.z*c)
    def rotate_x(self, a):
        r = math.radians(a)
        c, s = math.cos(r), math.sin(r)
        return Vector3(self.x, self.y*c - self.z*s, self.y*s + self.z*c)
    def rotate_z(self, a):
        r = math.radians(a)
        c, s = math.cos(r), math.sin(r)
        return Vector3(self.x*c - self.y*s, self.x*s + self.y*c, self.z)

# ==================== 3D对象基类 ====================

class Object3D:
    def __init__(self, engine):
        self.engine = engine
        self.x, self.y, self.z = 0, 0, 0
        self.rx = self.ry = self.rz = 0
        self.visible = True
        self.vertices = []
        self.faces = []
        self._placed = False
    
    def place(self, x=0, y=0, z=0, rx=0, ry=0, rz=0):
        self.x, self.y, self.z = x, y, z
        self.rx, self.ry, self.rz = rx, ry, rz
        if not self._placed:
            self.engine.objects.append(self)
            self._placed = True
        return self
    
    def add_vertex(self, x, y, z):
        self.vertices.append(Vector3(x, y, z))
        return len(self.vertices)-1
    
    def add_face(self, verts, col):
        self.faces.append({'vertices': verts.copy(), 'color': col})
    
    def transform(self):
        result = []
        for v in self.vertices:
            v = v.rotate_z(self.rz)
            v = v.rotate_y(self.ry)
            v = v.rotate_x(self.rx)
            v = Vector3(v.x+self.x, v.y+self.y, v.z+self.z)
            result.append(v)
        return result

# ==================== UI控件 ====================

class UIElement:
    def __init__(self, engine):
        self.engine = engine
        self.x, self.y = 0, 0
        self.visible = True
        self._placed = False
    
    def place(self, x=0, y=0):
        self.x, self.y = x, y
        if not self._placed:
            self.engine.ui_elements.append(self)
            self._placed = True
        return self

class ui:
    class Text(UIElement):
        def __init__(self, engine, text="", font_size=24, col=color.white()):
            super().__init__(engine)
            self.text = text
            self.font_size = font_size
            self.color = col
            self.id = None
        
        def set_text(self, text):
            self.text = text
            if self.id:
                self.engine.canvas.itemconfig(self.id, text=text)
        
        def render(self, canvas):
            if not self.visible or not self.text:
                return
            
            if self.id is None:
                self.id = canvas.create_text(
                    self.x, self.y,
                    anchor='nw',
                    text=self.text,
                    fill=self.color.to_hex(),
                    font=('Arial', self.font_size)
                )
            else:
                canvas.coords(self.id, self.x, self.y)
                canvas.itemconfig(self.id, text=self.text, 
                                 fill=self.color.to_hex(),
                                 font=('Arial', self.font_size))
    
    class Button(UIElement):
        def __init__(self, engine, text="", width=100, height=40,
                     bg=color.gray(), fg=color.white(), command=None):
            super().__init__(engine)
            self.text = text
            self.width = width
            self.height = height
            self.bg = bg
            self.fg = fg
            self.command = command
            self.rect_id = None
            self.text_id = None
            self._bound = False
        
        def place(self, x=0, y=0):
            super().place(x, y)
            self._bind_events()
            return self
        
        def _bind_events(self):
            if self._bound:
                return
            self._bound = True
            def on_click(e):
                if self.visible and self.command:
                    if (self.x <= e.x <= self.x + self.width and
                        self.y <= e.y <= self.y + self.height):
                        self.command()
            self.engine.root.bind('<Button-1>', on_click)
        
        def render(self, canvas):
            if not self.visible:
                if self.rect_id:
                    canvas.delete(self.rect_id)
                    self.rect_id = None
                if self.text_id:
                    canvas.delete(self.text_id)
                    self.text_id = None
                return
            
            if self.rect_id is None:
                self.rect_id = canvas.create_rectangle(
                    self.x, self.y,
                    self.x + self.width, self.y + self.height,
                    fill=self.bg.to_hex(), outline=''
                )
            else:
                canvas.coords(self.rect_id, self.x, self.y,
                             self.x + self.width, self.y + self.height)
                canvas.itemconfig(self.rect_id, fill=self.bg.to_hex())
            
            text_x = self.x + self.width / 2
            text_y = self.y + self.height / 2
            
            if self.text_id is None:
                self.text_id = canvas.create_text(
                    text_x, text_y,
                    text=self.text,
                    fill=self.fg.to_hex(),
                    font=('Arial', 14),
                    anchor='center'
                )
            else:
                canvas.coords(self.text_id, text_x, text_y)
                canvas.itemconfig(self.text_id, text=self.text, fill=self.fg.to_hex())

# ==================== 3D物体 ====================

class object:
    class Cube(Object3D):
        def __init__(self, engine, width=1, height=1, length=1, col=color.green()):
            super().__init__(engine)
            self.width = width
            self.height = height
            self.length = length
            self.color = col
            self._create_mesh()
        
        def _create_mesh(self):
            w, h, l = self.width/2, self.height/2, self.length/2
            
            self.add_vertex(-w, -h, -l)  # 0
            self.add_vertex( w, -h, -l)  # 1
            self.add_vertex( w,  h, -l)  # 2
            self.add_vertex(-w,  h, -l)  # 3
            self.add_vertex(-w, -h,  l)  # 4
            self.add_vertex( w, -h,  l)  # 5
            self.add_vertex( w,  h,  l)  # 6
            self.add_vertex(-w,  h,  l)  # 7
            
            self.add_face([0,1,2], color.red())
            self.add_face([0,2,3], color.red())
            self.add_face([4,6,5], color.blue())
            self.add_face([4,7,6], color.blue())
            self.add_face([0,3,7], color.green())
            self.add_face([0,7,4], color.green())
            self.add_face([1,5,6], color.yellow())
            self.add_face([1,6,2], color.yellow())
            self.add_face([0,4,5], color.purple())
            self.add_face([0,5,1], color.purple())
            self.add_face([3,2,6], color.cyan())
            self.add_face([3,6,7], color.cyan())
    
    class Plane(Object3D):
        def __init__(self, engine, width=10, length=10, col=color.dark_gray()):
            super().__init__(engine)
            self.width = width
            self.length = length
            self.color = col
            self._create_mesh()
        
        def _create_mesh(self):
            w, l = self.width/2, self.length/2
            self.add_vertex(-w, 0, -l)
            self.add_vertex( w, 0, -l)
            self.add_vertex( w, 0,  l)
            self.add_vertex(-w, 0,  l)
            self.add_face([0,1,2], self.color)
            self.add_face([0,2,3], self.color)

# ==================== 相机 ====================

class camera:
    def __init__(self, engine):
        self.engine = engine
        self.x, self.y, self.z = 0, 0, -10
        self.rx, self.ry, self.rz = 0, 0, 0
        self.fov = 60
        engine.camera = self
    
    def place(self, x=0, y=0, z=-10, rx=0, ry=0, rz=0):
        self.x, self.y, self.z = x, y, z
        self.rx, self.ry, self.rz = rx, ry, rz
        return self
    
    def project(self, point, w, h):
        rel = point - Vector3(self.x, self.y, self.z)
        rel = rel.rotate_z(-self.rz)
        rel = rel.rotate_y(-self.ry)
        rel = rel.rotate_x(-self.rx)
        if rel.z <= 0.1:
            return None
        aspect = w / h
        fov_rad = math.radians(self.fov)
        scale = 1 / (rel.z * math.tan(fov_rad/2))
        x = rel.x * scale * aspect
        y = rel.y * scale
        return ((x+1)*w/2, (1-y)*h/2, rel.z)

# ==================== 引擎 ====================

class engine:
    def __init__(self, width=1024, height=768, title="Turtle3D", bg="#1a1a2a", fps=60):
        self.width, self.height, self.title, self.bg, self.fps = width, height, title, bg, fps
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.objects = []
        self.ui_elements = []
        self.camera = None
        self.running = True
        self.frame = 0
        self.last_time = time.time()
        self.fps_display = 0
        self.angle = 0
        self._show_info = False
        
        self._key_handlers = {}
        
        self.root.bind('<KeyPress>', self._on_key_press)
        self.canvas.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        self.update()
    
    def bind(self, key, callback):
        self._key_handlers[key.lower()] = callback
        print(f"⌨️ 已绑定按键: {key}")
        return self
    
    def _on_key_press(self, event):
        key = event.keysym.lower()
        if key in self._key_handlers:
            self._key_handlers[key](event)
        else:
            print(f"⚠️ 按键 '{key}' 未绑定，无反应")
    
    def info(self, show=None):
        """切换FPS显示状态"""
        if show is not None:
            self._show_info = show
        else:
            self._show_info = not self._show_info
        
        # 立即刷新显示
        if self._show_info:
            # 显示FPS - 强制删除旧的再创建
            self.canvas.delete('fps_text')
            fps_color = "#0f0" if self.fps_display >= 50 else "#ff0" if self.fps_display >= 30 else "#f00"
            self.canvas.create_text(10, 10, anchor='nw',
                text=f"FPS: {self.fps_display} | 3D: {len(self.objects)} | UI: {len(self.ui_elements)}",
                fill=fps_color, font=('Consolas', 12), tags='fps_text')
        else:
            self.canvas.delete('fps_text')
        
        print(f"📊 FPS显示: {'开启' if self._show_info else '关闭'}")
        return self._show_info
    
    def render(self):
        if not self.camera:
            return
        
        self.frame += 1
        if time.time() - self.last_time >= 1:
            self.fps_display = self.frame
            self.frame = 0
            self.last_time = time.time()
        
        self.canvas.delete('3d_object')
        
        all_faces = []
        
        for obj in self.objects:
            if not obj.visible:
                continue
            transformed = obj.transform()
            projected = [self.camera.project(v, self.width, self.height) for v in transformed]
            
            for face in obj.faces:
                pts = []
                depths = []
                ok = True
                for idx in face['vertices']:
                    if idx < len(projected) and projected[idx]:
                        pts.append((projected[idx][0], projected[idx][1]))
                        depths.append(projected[idx][2])
                    else:
                        ok = False
                        break
                if ok and len(pts) >= 3:
                    flat = []
                    for p in pts:
                        flat.extend(p)
                    all_faces.append({
                        'pts': flat,
                        'depth': sum(depths)/len(depths),
                        'color': face['color'].to_hex()
                    })
        
        all_faces.sort(key=lambda x: x['depth'], reverse=True)
        
        for face in all_faces:
            try:
                self.canvas.create_polygon(face['pts'], fill=face['color'], 
                                           outline='', tags='3d_object')
            except:
                pass
        
        for ui_elem in self.ui_elements:
            ui_elem.render(self.canvas)
        
        # 如果FPS显示开启，更新显示
        if self._show_info:
            self.canvas.delete('fps_text')
            fps_color = "#0f0" if self.fps_display >= 50 else "#ff0" if self.fps_display >= 30 else "#f00"
            self.canvas.create_text(10, 10, anchor='nw',
                text=f"FPS: {self.fps_display} | 3D: {len(self.objects)} | UI: {len(self.ui_elements)}",
                fill=fps_color, font=('Consolas', 12), tags='fps_text')
    
    def animate(self):
        self.angle += 2
        for obj in self.objects:
            if isinstance(obj, object.Cube):
                obj.ry = self.angle
                obj.rx = self.angle * 0.3
    
    def update(self):
        if self.running:
            self.animate()
            self.render()
            self.root.after(int(1000/self.fps), self.update)
    
    def start(self):
        print("🐢 Turtle3D Engine Started")
        print("⚠️ 必须用 game.bind('key', callback) 绑定按键才能响应！")
        self.root.mainloop()
    
    def stop(self):
        self.running = False
        self.root.quit()


# ==================== 测试 ====================

if __name__ == "__main__":
    game = engine(1024, 768, "Turtle3D", "#1a1a2a", fps=60)
    
    # 相机
    cam = camera(game).place(x=0, y=0, z=-5, rx=0, ry=0, rz=0)
    
    # 3D物体
    cube = object.Cube(game, width=1.5, height=1.5, length=1.5, col=color.red()).place(x=0, y=0, z=0)
    ground = object.Plane(game, width=6, length=6, col=color.dark_gray()).place(x=0, y=-0.9, z=0)
    
    # UI
    title = ui.Text(game, text="Turtle3D Engine", font_size=28, col=color.gold()).place(x=350, y=30)
    info_text = ui.Text(game, text="按 I 键切换FPS显示", font_size=16, col=color.cyan()).place(x=350, y=80)
    status = ui.Text(game, text="就绪", font_size=14, col=color.light_gray()).place(x=20, y=730)
    
    def on_click():
        print("🎯 按钮被点击！")
        status.set_text("按钮被点击了！")
    
    btn = ui.Button(game, text="点击我", width=120, height=40,
                    bg=color.blue(), fg=color.white(), command=on_click).place(x=460, y=680)
    
    # ===== 绑定按键 =====
    # 绑定 I 键 - 切换FPS显示
    game.bind('i', lambda e: game.info())
    
    # 绑定 R 键
    def on_r_press(e):
        status.set_text("按了 R 键！")
        print("📍 按了 R 键")
    game.bind('r', on_r_press)
    
    # 绑定方向键
    def move_left(e):
        cube.x -= 0.1
        status.set_text(f"立方体 x={cube.x:.1f}")
        print(f"📍 立方体 x={cube.x:.1f}")
    
    def move_right(e):
        cube.x += 0.1
        status.set_text(f"立方体 x={cube.x:.1f}")
        print(f"📍 立方体 x={cube.x:.1f}")
    
    game.bind('Left', move_left)
    game.bind('Right', move_right)
    
    print("\n" + "=" * 50)
    print("🐢 Turtle3D 启动")
    print("=" * 50)
    print("已绑定的按键:")
    print("  I - 切换FPS显示")
    print("  R - 测试按键")
    print("  ← → - 移动立方体")
    print("=" * 50 + "\n")
    
    game.start()
