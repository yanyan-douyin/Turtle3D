# 🐢 Turtle3D

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![tkinter](https://img.shields.io/badge/tkinter-built--in-orange)](https://docs.python.org/3/library/tkinter.html)

一个基于 Tkinter Canvas 的轻量级 3D 图形库，**无需安装 OpenGL** 即可创建简单的 3D 场景和交互应用。

---

## ✨ 特性

- 🎨 **纯 Python 实现** - 无需安装 OpenGL 或其他图形库
- 📦 **简单的 API** - 类似 Tkinter 的使用方式，上手极快
- 🎮 **内置 UI 控件** - 支持文字、按钮等 2D 控件叠加
- ⌨️ **键盘事件绑定** - 灵活的按键响应系统，适合做交互游戏
- 🎯 **3D 物体** - 立方体、平面等基础 3D 物体，可扩展
- 📊 **性能监控** - 内置 FPS 显示功能
- 🔄 **自动动画** - 支持物体旋转、平移动画
- 🪶 **轻量级** - 整个库只有一个文件，方便嵌入其他项目

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/yanyan-douyin/Turtle3D.git

# 进入目录
cd Turtle3D

# 安装可选依赖（字体渲染增强，不装也不影响核心功能）
pip install Pillow
