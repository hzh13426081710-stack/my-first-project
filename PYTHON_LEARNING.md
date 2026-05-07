# Python 实践学习路线

这个项目很适合用“小游戏改造法”学习 Python：你每次只改一个小功能，马上运行游戏看到结果。比单独刷语法更容易形成直觉。

## 运行项目

先在项目目录中安装依赖：

```powershell
pip install -r requirements.txt
```

运行贪吃蛇：

```powershell
python snake_game.py
```

运行射击游戏：

```powershell
python shooter_game.py
```

运行小鹤双拼练习游戏：

```powershell
python flypy_falling_game.py
```

## 推荐学习顺序

1. 先学 `snake_game.py`

   它结构最短，适合入门。重点看这些概念：

   - 常量：`WINDOW_WIDTH`、`CELL_SIZE`、`FPS`
   - 数据类：`@dataclass` 和 `Point`
   - 列表：`self.snake.insert(0, new_head)`、`self.snake.pop()`
   - 条件判断：撞墙、撞自己、吃食物
   - 类和方法：`SnakeGame.reset()`、`SnakeGame.update()`、`SnakeGame.draw()`
   - 主循环：`handle_input()` -> `update()` -> `draw()`

2. 再学 `shooter_game.py`

   它会引入更多“真实游戏”写法：

   - 浮点坐标和速度
   - `dt` 时间增量
   - 鼠标输入
   - 敌人列表
   - 碰撞检测
   - 难度随时间增加

3. 最后学 `flypy_falling_game.py`

   它更接近一个完整工具，适合练：

   - 字典数据
   - 关卡配置
   - 文本输入
   - 游戏状态管理
   - 中文内容和编码问题

## 每天一个小练习

### 第 1 天：改常量

在 `snake_game.py` 里修改这些值：

```python
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 540
CELL_SIZE = 24
FPS = 10
```

练习目标：理解变量、整数、除法、网格大小和帧率。

### 第 2 天：改颜色

修改颜色常量，例如：

```python
SNAKE_HEAD_COLOR = (110, 231, 183)
FOOD_COLOR = (248, 113, 113)
```

练习目标：理解元组 `tuple`，以及 RGB 颜色。

### 第 3 天：加暂停功能

目标：按 `P` 暂停，再按一次继续。

提示：

- 可以增加一个状态：`"paused"`
- 在 `handle_input()` 里监听 `pygame.K_p`
- 在 `draw()` 里给暂停状态画提示层

### 第 4 天：加穿墙模式

目标：蛇撞到右边界后从左边出来。

提示：

```python
new_head = Point(new_head.x % GRID_WIDTH, new_head.y % GRID_HEIGHT)
```

练习目标：理解取模 `%`。

### 第 5 天：增加特殊食物

目标：随机出现一个加 3 分的特殊食物。

练习目标：理解多个对象、随机数、条件分支。

### 第 6 天：保存最高分

目标：把最高分写入本地文件，下次运行还能读取。

练习目标：理解文件读写、异常处理。

### 第 7 天：重构代码

目标：把重复逻辑整理成小函数。

练习目标：理解函数职责，以及“一个函数只做一件事”的思想。

## 怎么读一段 Python 代码

建议按这个顺序读：

1. 先看文件顶部的 `import`，知道用了哪些库。
2. 再看常量，知道程序有哪些固定配置。
3. 找 `if __name__ == "__main__"`，确认程序从哪里启动。
4. 找主类，比如 `SnakeGame`。
5. 找主循环，比如 `run()`。
6. 顺着主循环看输入、更新、绘制。
7. 最后再看细节函数。

## 注释原则

中文注释不是越多越好。好的注释应该解释：

- 为什么这样写
- 某个变量代表什么
- 某段逻辑在游戏里对应什么行为
- Python 语法背后的用途

不太好的注释通常只是重复代码，例如：

```python
self.score += 1  # 分数加 1
```

更有帮助的写法是：

```python
self.score += 1  # 吃到普通食物后奖励 1 分。
```

## 下一步建议

先完成“第 3 天：加暂停功能”。这个任务很小，但会让你真正理解状态机：开始、运行、暂停、结束。
