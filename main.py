import pygame, sys, os, random, time
from pygame.locals import * # Truy cập đến các hằng số
from pygame.sprite import Group

pygame.init() # Start point

# ======================= CONSTANTS ======================= #

SIZE = WIN_WIDTH, WIN_HEIGHT = (1000,600)     # Khung hình
DISPLAYSURF = pygame.display.set_mode(SIZE)   # Thiết lập khung hình
FPS = pygame.time.Clock()                     # Thiết lập FPS
BASE_SPEED = 7                                # Tốc độ player
BASE_HEALTH = 300                             # Thanh máu
GREEN = (0,230,0)                             # Màu thanh máu còn lại
RED = (230,0,0)                               # Màu thanh máu bị mất
RED_OVERLAY = (255, 50, 50)                   # Màu layer khi bị thương
FONT = pygame.font.SysFont('Arial', 40)       # Thiết lập font chữ để render

# Nạp asset background
BG = pygame.image.load(os.path.join('Assets','GrassField.png')).convert()



# ======================= CLASSES ======================= #

'''
Lớp Character gồm những thuộc tính cơ bản nhất của các nhân vật xuất hiện trong game
Kế thừa từ class Sprite giúp nhóm các đối tượng kế thừa từ class này
'''
class Character(pygame.sprite.Sprite):
    def __init__(self, type_: str) -> None:
        # Gọi hàm khởi tạo từ lớp Sprite để kế thừa toàn bộ function
        super().__init__()
        # Nạp chu trình di chuyển cho các nhân vật nói chung
        self.walk_anim = [
            pygame.image.load(os.path.join('Assets', type_, f'{type_}_Standing.png')).convert_alpha(),
            pygame.image.load(os.path.join('Assets', type_, f'{type_}_R_Step.png')).convert_alpha(),
            pygame.image.load(os.path.join('Assets', type_, f'{type_}_Standing.png')).convert_alpha(),
            pygame.image.load(os.path.join('Assets', type_, f'{type_}_L_Step.png')).convert_alpha()
        ]
        self.surf = pygame.Surface((100,150))   # Đồng bộ kích thước characters
        self.dir = 1                            # 1 - right   -1 - left
        self.step_count = 0                     # Dựa vào đây để xuất trạng thái trong 1 chu trình di chuyển

class Player(Character):
    def __init__(self) -> None:
        Character.__init__(self, 'Hero')
        # Nạp trạng thái bị thương khi chạm vào zombie
        self.taken_dam = pygame.image.load(os.path.join('Assets', 'Hero', 'Hero_Taken_Damage.png')).convert_alpha()
        # Tạo khung bao quanh nhân vật xử lý vật lý và hiển thị, cho nhân vật xuất hiện ở giữa màn hình
        self.rect = self.surf.get_rect(center = (WIN_WIDTH/2, WIN_HEIGHT/2))
        # Thiết lập tốc độ di chuyển ban đầu
        self.speed_x = BASE_SPEED
        self.speed_y = BASE_SPEED
        # Thiết lập lượng máu ban đầu, khi hiển thị tính theo pixel
        self.health = BASE_HEALTH

    def move(self):

        # Lấy trạng thái các phím
        pressed_key = pygame.key.get_pressed()

        # Nếu đang quay sang phải mà nhấn di chuyển sang trái thì bắt đầu 1 chu trình di chuyển mới
        if self.rect.left > 0 and pressed_key[K_LEFT]:
            if self.dir == 1:
                self.step_count = 0
                self.dir *= -1
            self.step_count += 1
            self.rect.move_ip(-self.speed_x,0)
        
        if self.rect.right < WIN_WIDTH and pressed_key[K_RIGHT]:
            if self.dir == -1:
                self.step_count = 0
                self.dir *= -1
            self.step_count += 1
            self.rect.move_ip(self.speed_x,0)

        if self.rect.top > 0 and pressed_key[K_UP]:
            self.rect.move_ip(0,-self.speed_y)
            self.step_count += 1

        if self.rect.bottom < WIN_HEIGHT and pressed_key[K_DOWN]:
            self.rect.move_ip(0,self.speed_y)
            self.step_count += 1

        # Nếu đã được 60 bước thì reset về 0 để không bị quá tải bộ nhớ khi đếm số bước
        if self.step_count >= 59:
            self.step_count = 0



class Zombie(Character):
    def __init__(self):
        Character.__init__(self, 'Zombie')
        # Tạo khung bao quanh để xử lý va chạm, xuất hiện ở vị trí ngẫu nhiên
        self.rect = self.surf.get_rect(center = (random.randint(50, WIN_WIDTH-50), random.randint(75, WIN_HEIGHT-75)))
        # Tốc độ di chuyển là ngẫu nhiên
        self.x_speed = random.randint(1,6)
        self.y_speed = random.randint(1,6)

    def move(self):

        if self.step_count >= 59:
            self.step_count = 0

        # Để zombie tự di chuyển
        self.rect.move_ip(self.x_speed, self.y_speed)

        # Out of bounds -> Quay đầu
        if self.rect.right > WIN_WIDTH or self.rect.left < 0:
            self.x_speed *= -1
            self.dir *= -1

        if self.rect.bottom > WIN_HEIGHT or self.rect.top < 0:
            self.y_speed *= -1

        self.step_count += 1



# ======================= GAME FUNCTIONS ======================= #
def draw_window(disp, bg, player, zombies):

    # Draw background
    disp.blit(bg, (0,0))

    # Draw Zombies
    for zombie in zombies:
        # Giới hạn 0 <= step_count <= 59, di chuyển 15 frame thì chuyển trạng thái 1 lần
        current_zombie_sprite = zombie.walk_anim[zombie.step_count//15]
        if zombie.dir == -1:
            current_zombie_sprite = pygame.transform.flip(current_zombie_sprite, True, False)
        disp.blit(current_zombie_sprite, zombie.rect)

    # Check for collision & Draw player
    '''
    Nếu đang va chạm thì trạng thái là taken_dam còn không thì sẽ xuất theo số bước di chuyển
    Khi đã chọn xong thì qua khối if tiếp theo sẽ lật ảnh nếu cần
    '''
    if pygame.sprite.spritecollideany(player, zombies):
        player.health -= 1
        current_player_sprite = player.taken_dam
        # Tạo hiệu ứng lớp phủ khi va chạm vs zombies
        disp.fill(RED_OVERLAY, special_flags = BLEND_MULT)
    else:
        current_player_sprite = player.walk_anim[player.step_count//15]
        
    # Không thể lồng khối này vào trên vì phải có ảnh để lật
    if player.dir == -1:
        current_player_sprite = pygame.transform.flip(current_player_sprite, True, False)
    # Phủ lớp màu lên mới vẽ
    disp.blit(current_player_sprite, player.rect)

    # Draw Health Bar: Vẽ HCN
    pygame.draw.rect(disp, GREEN, (20,20,player.health,20))
    pygame.draw.rect(disp, RED, (player.health+20,20,BASE_HEALTH-player.health,20))

    # Draw current score
    score_text = FONT.render(f'TIME SURVIVED : {score//60}', True, (200, 200, 200))
    disp.blit(score_text,(WIN_WIDTH/2,20))

    pygame.display.update()

# On lose
def game_over():
    # Text
    game_over_text = FONT.render('STUPID', True, (200,200,200))
    score_text = FONT.render(f'SURVIVED FOR {score//60} SECONDS',True, (200,200,200))
    zombie_count_text = FONT.render(f'ZOMBIE COUNT: {zombie_cnt}',True, (200,200,200))

    # Phủ 1 lớp màu đen lên để hiển thị
    DISPLAYSURF.fill((0,0,0))
    DISPLAYSURF.blit(game_over_text, (WIN_WIDTH/2 - game_over_text.get_width()/2, WIN_HEIGHT/2 - game_over_text.get_height()/2))
    DISPLAYSURF.blit(score_text, (WIN_WIDTH/2-score_text.get_width()/2, WIN_HEIGHT/2 + score_text.get_height() * 1.5))
    DISPLAYSURF.blit(zombie_count_text, (WIN_WIDTH/2-zombie_count_text.get_width()/2, WIN_HEIGHT/2 + zombie_count_text.get_height() * 2.5))

    # Xử lý tất cả nhân vật còn trong bộ nhớ - Clear
    for character in My_Sprites:
        character.kill()

    pygame.display.update()
    time.sleep(6)
    pygame.quit()
    sys.exit()



# ======================= INITIALIZE ======================= #

player_ = Player()
zombie_ = Zombie()
zombie_cnt = 1

# Nhóm các zombie lại để dễ xử lý
zombies = pygame.sprite.Group()
zombies.add(zombie_)

# Nhóm lại để tiện cho di chuyển tất cả các đối tượng
My_Sprites = pygame.sprite.Group()
My_Sprites.add(zombies, player_)
score = 0



# ======================= USER EVENTS ======================= #

# Định nghĩa các sự kiện tùy chỉnh khi đạt 1 điều kiện hay thời gian của riêng mình để xử lý tác vụ
SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 8000)



# ======================= GAME LOOP ======================= #
while True:
    # Lấy danh sách các sự kiện diễn ra trong của sổ hiển thị
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_ENEMY:
            new_zombie = Zombie()
            zombies.add(new_zombie)
            My_Sprites.add(new_zombie)
            zombie_cnt += 1

    score += 1

    if player_.health <= 0:
        game_over()

    for character in My_Sprites:
        character.move()

    draw_window(DISPLAYSURF, BG, player_, zombies)

    FPS.tick(60)