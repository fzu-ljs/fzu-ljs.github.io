import pygame
import sys
import random
import time

# 设置窗口大小
width, height = 1040, 780
screen = pygame.display.set_mode((width, height))

# 设置窗口标题
pygame.display.set_caption("羊了个羊游戏菜单")

# 设置颜色
LIGHT_BLUE = (100, 149, 237)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 初始化字体系统
pygame.font.init()

# 设置字体和大小
font = pygame.font.Font(None, 36)

# 菜单项
menu_items = ["Easy", "Rules", "developing...", "Exit"]
item_height = font.get_height() * 7

# 用于存储鼠标位置和菜单项状态
mouse_pos = pygame.mouse.get_pos()
selected_item = None

# 游戏状态变量
game_over = False

# 底部矩形框中的图片列表
box_images = []

# 定义图案图片尺寸
TILE_SIZE = 70

# 加载图案图片
patterns = [pygame.image.load(f"pattern{i}.png") for i in range(1, 12)]
patterns = [pygame.transform.scale(p, (TILE_SIZE, TILE_SIZE)) for p in patterns]

# 定义间距
SPACING = 35

# 定义底部矩形框
BOX_WIDTH = 7 * (TILE_SIZE + SPACING)
BOX_HEIGHT = TILE_SIZE
box_rect = pygame.Rect((width - BOX_WIDTH) // 2, height - BOX_HEIGHT - 60, BOX_WIDTH, BOX_HEIGHT)

# 初始化九宫格图案为两层
layers = [[[random.choice(patterns), random.choice(patterns)] for _ in range(5)] for _ in range(5)]

# 倒计时相关
start_time = None
total_time = 60  # 总时间60秒
remaining_time = total_time

# 得分相关
score = 0
high_scores = []

# 初始化音频模块并加载主菜单音乐
pygame.mixer.init()
menu_music = pygame.mixer.Sound("bgm2.mp3")
menu_music.play(-1)


def draw_game_over_screen():
    global high_scores
    game_over_screen = pygame.Surface((width, height))
    game_over_screen.fill((150, 150, 150))
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("Game Over!", True, BLACK)
    final_score_text = font.render(f"Final Score: {score}", True, BLACK)
    restart_button = font.render("Restart", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 80))
    final_score_rect = final_score_text.get_rect(center=(width // 2, height // 2 - 30))
    restart_rect = restart_button.get_rect(center=(width // 2, height // 2 + 20))
    game_over_screen.blit(game_over_text, game_over_rect)
    game_over_screen.blit(final_score_text, final_score_rect)
    pygame.draw.rect(game_over_screen, WHITE, restart_rect)
    pygame.draw.rect(game_over_screen, BLACK, restart_rect, 2)
    game_over_screen.blit(restart_button, restart_rect)

    # 更新并显示排行榜
    high_scores.append(score)
    high_scores.sort(reverse=True)
    high_scores = high_scores[:5]
    high_score_display = font.render("High Scores:", True, BLACK)
    y = height // 2 + 80
    for index, s in enumerate(high_scores):
        score_display = font.render(f"{index + 1}. {s}", True, BLACK)
        game_over_screen.blit(score_display, (width // 2 - score_display.get_width() // 2, y))
        y += score_display.get_height() + 10

    return game_over_screen, restart_rect


def check_game_over():
    global game_over
    if len(box_images) == 7:
        has_three_same = False
        for pattern in patterns:
            count = box_images.count(pattern)
            if count >= 3:
                has_three_same = True
                break
        if not has_three_same:
            game_over = True
    return game_over


def draw_patterns():
    # 加载背景图片
    background_img = pygame.image.load("海底背景图.png")
    # 调整背景图片大小以填满窗口
    background_img = pygame.transform.scale(background_img, (width, height))

    center_x = width // 2
    center_y = height // 2
    start_x = center_x - (5 * (TILE_SIZE + SPACING)) // 2
    start_y = center_y - (5 * (TILE_SIZE + SPACING)) // 2

    # 在窗口绘制背景图
    screen.blit(background_img, (0, 0))

    for row in range(5):
        for col in range(5):
            top_pattern = layers[row][col][0]
            bottom_pattern = layers[row][col][1]
            x = start_x + col * (TILE_SIZE + SPACING)
            y = start_y + row * (TILE_SIZE + SPACING)
            # 交错显示
            # 先绘制第二层，半透明显示
            bottom_pattern.set_alpha(255)
            screen.blit(bottom_pattern, (x, y-20))
            # 再绘制第一层
            screen.blit(top_pattern, (x, y))




def play_game():

    global game_over, score, box_images, layers, start_time
    # 停止主菜单音乐
    menu_music.stop()
    # 加载游戏音乐
    game_music = pygame.mixer.Sound("bgm1.mp3")
    game_music.play(-1)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    pos = pygame.mouse.get_pos()
                    center_x = width // 2
                    center_y = height // 2
                    start_x = center_x - (5 * (TILE_SIZE + SPACING)) // 2
                    start_y = center_y - (5 * (TILE_SIZE + SPACING)) // 2
                    for row in range(5):
                        for col in range(5):
                            rect = pygame.Rect(start_x + col * (TILE_SIZE + SPACING), start_y + row * (TILE_SIZE + SPACING), TILE_SIZE,
                                               TILE_SIZE)
                            if rect.collidepoint(pos) and layers[row][col][0] is not None:
                                selected_pattern = layers[row][col][0]
                                layers[row][col][0] = layers[row][col][1]
                                layers[row][col][1] = random.choice(patterns)
                                # 计算矩形框中每个图片的位置，从框的左上角开始
                                box_index = len(box_images)
                                if box_index < 7:
                                    box_x = box_rect.x + SPACING + box_index * (TILE_SIZE)
                                    box_y = box_rect.y + SPACING
                                    # 将被点击的图片添加到矩形框的正确位置
                                    box_images.append(selected_pattern)
                                    if len(box_images) >= 3:
                                        for pattern in patterns:
                                            count = box_images.count(pattern)
                                            if count >= 3:
                                                temp_list = []
                                                for img in box_images:
                                                    if img == pattern:
                                                        temp_list.append(img)
                                                for _ in temp_list:
                                                    box_images.remove(pattern)
                                                score += 10
                                    if len(box_images) == 7:
                                        game_over = check_game_over()
                                        if game_over:
                                            break
                        if game_over:
                            break

        if not game_over:
            if start_time is None:
                start_time = time.time()
            elapsed_time = time.time() - start_time
            remaining_time = total_time - elapsed_time
            if remaining_time <= 0:
                game_over = True

        if game_over:
            game_over_screen, restart_rect = draw_game_over_screen()
            screen.blit(game_over_screen, (0, 0))
            pygame.display.flip()
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        game_over = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if restart_rect.collidepoint(pos):
                            # 重新开始游戏
                            game_over = False
                            score = 0
                            box_images.clear()
                            layers = [[[random.choice(patterns), random.choice(patterns)] for _ in range(5)] for _ in
                                      range(5)]
                            start_time = None
                            # 停止游戏音乐，准备返回主菜单时播放主菜单音乐
                            game_music.stop()
                            menu_music.play(-1)
                            return False
            continue

        screen.fill(WHITE)
        draw_patterns()
        x = box_rect.x + SPACING
        y_box = box_rect.y + SPACING
        for image in box_images:
            screen.blit(image, (x, y_box))
            x += TILE_SIZE + SPACING

        font = pygame.font.Font(None, 36)
        if not game_over and start_time is not None:
            time_text = font.render(f"Time: {int(remaining_time)}s", True, BLACK)
            screen.blit(time_text, (10, 10))
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 50))

        pygame.display.flip()

    # 停止游戏音乐
    game_music.stop()
    pygame.quit()
    return False


# 显示游戏规则的函数
def show_rules():
    global running  # 使用全局变量来控制主循环的运行状态
    print("Game Rules")
    # 清除屏幕
    screen.fill(LIGHT_BLUE)
    # 规则文本
    rules_text = "Game Rules:\n- try hard to find the same pictures\n- Every three identical pictures can be eliminated.\n- The more pictures are eliminated within the limited time, the higher the score."
    # 将文本分割成行
    lines = rules_text.split('\n')
    # 计算文本的总高度
    total_height = font.get_height() * len(lines)
    # 设置文本的起始位置
    y = height // 2 - total_height // 2
    # 渲染每行文本
    for line in lines:
        text = font.render(line, True, BLACK)
        text_rect = text.get_rect(center=(width // 2, y))
        screen.blit(text, text_rect)
        y += font.get_height()  # 更新下一行的起始位置

    # 绘制返回按钮
    back_button = font.render("Back", True, BLACK)
    back_rect = back_button.get_rect(center=(width - 100, height - 50))
    pygame.draw.rect(screen, WHITE, back_rect)
    pygame.draw.rect(screen, BLACK, back_rect, 2)  # 绘制边框
    screen.blit(back_button, back_rect)  # 将文字绘制到按钮上

    # 更新屏幕显示
    pygame.display.flip()

    # 等待用户点击返回按钮
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return  # 返回主菜单


# 确认退出的函数
def confirm_exit():
    # 创建一个临时窗口用于显示退出确认对话框
    confirm_screen = pygame.display.set_mode((width, height))
    confirm_screen.fill(WHITE)
    confirm_font = pygame.font.Font(None, 48)
    confirm_text = confirm_font.render("Are you sure you want to exit?", True, BLACK)
    confirm_rect = confirm_text.get_rect(center=(width // 2, height // 2))
    confirm_screen.blit(confirm_text, confirm_rect)

    # 设置按钮的文字和背景颜色
    button_color = (200, 200, 200)  # 按钮背景颜色
    text_color = BLACK  # 按钮文字颜色

    # 绘制两个按钮
    yes_rect = pygame.Rect(width // 2 - 250, height // 2 + 50, 100, 50)
    no_rect = pygame.Rect(width // 2 + 150, height // 2 + 50, 100, 50)
    pygame.draw.rect(confirm_screen, button_color, yes_rect)
    pygame.draw.rect(confirm_screen, button_color, no_rect)
    yes_text = confirm_font.render("Yes", True, text_color)
    no_text = confirm_font.render("No", True, text_color)
    yes_text_rect = yes_text.get_rect(center=yes_rect.center)
    no_text_rect = no_text.get_rect(center=no_rect.center)
    confirm_screen.blit(yes_text, yes_text_rect)
    confirm_screen.blit(no_text, no_text_rect)
    pygame.display.flip()

    # 等待用户响应
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    return True  # 用户点击了“是”
                elif no_rect.collidepoint(event.pos):
                    return False  # 用户点击了“否”

    pygame.quit()
    sys.exit()


# 游戏主循环
running = True
while running:
    if not game_over:
        # 检查事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查是否点击了菜单项
                mouse_pos = event.pos
                for i, item in enumerate(menu_items):
                    rect = pygame.Rect(50, i * item_height, width - 100, item_height)
                    if rect.collidepoint(event.pos):
                        selected_item = i
                        if i == 3:  # Exit
                            if confirm_exit():
                                running = False  # 用户确认退出
                        elif i == 1:  # Rules
                            show_rules()
                        elif i == 2:  # Settings
                            # 这里可以添加设置界面的代码
                            pass
                        elif i == 0:  # Play Game
                            # 进入游戏逻辑，这里可以调用游戏函数
                            game_over = play_game()
    else:
        # 绘制游戏结束界面
        screen.fill(LIGHT_BLUE)
        game_over_text = font.render("Game Over", True, BLACK)
        restart_button = font.render("Restart", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 50))
        restart_rect = restart_button.get_rect(center=(width // 2, height // 2))
        screen.blit(game_over_text, game_over_rect)
        pygame.draw.rect(screen, WHITE, restart_rect)
        pygame.draw.rect(screen, BLACK, restart_rect, 2)
        screen.blit(restart_button, restart_rect)
        pygame.display.flip()
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_for_input = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if restart_rect.collidepoint(pos):
                        # 重新开始游戏
                        game_over = False
                        score = 0
                        box_images.clear()
                        layers = [[[random.choice(patterns), random.choice(patterns)] for _ in range(5)] for _ in
                                  range(5)]
                        start_time = None
                        waiting_for_input = False

    # 填充背景色为较淡的蓝色
    screen.fill((100, 149, 237))  # 使用 RGB 值设置背景为较淡的蓝色

    # 绘制菜单项
    for i, item in enumerate(menu_items):
        rect = pygame.Rect(50, i * item_height, width - 100, item_height)
        color = WHITE if selected_item == i else LIGHT_BLUE
        pygame.draw.rect(screen, color, rect)
        text = font.render(item, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # 更新屏幕显示
    pygame.display.flip()

# 退出 pygame
pygame.quit()
sys.exit()