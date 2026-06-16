import os
import sys
import pygame as pg
import random
import time

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0)
}

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect または 爆弾Rect
    戻り値：真偽値タプル（横方向、縦方向）
    画面内：True、画面外：False
    """
    yk, tt = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yk = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tt = False
    return yk, tt

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数：screen（描画対象の画面Surface）
    """
    Bbg_img = pg.Surface((WIDTH, HEIGHT))     
    pg.draw.rect(Bbg_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    Bbg_img.set_alpha(180) 
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    cry_kk_l = pg.image.load("fig/8.png")
    cry_kk_r = pg.transform.flip(cry_kk_l, True, False)
    Bbg_img.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
    Bbg_img.blit(cry_kk_l, (WIDTH // 2 - txt.get_width() // 2 - cry_kk_l.get_width(), HEIGHT // 2 - txt.get_height() // 2))
    Bbg_img.blit(cry_kk_r, (WIDTH // 2 + txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
    screen.blit(Bbg_img, (0, 0))
    pg.display.update()
    time.sleep(5)
  
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさを変えた爆弾Surfaceのリストと、
    加速度のリストを準備して返す関数

    引数:
        なし

    戻り値:
        tuple[list[pg.Surface], list[int]]: 
            - list[pg.Surface]: 10段階のサイズ(20*r, 20*r)の爆弾Surfaceのリスト
            - list[int]: 1から10までの加速度が入ったリスト
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        # 背景の黒を透明化
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0
    vx, vy = +1, +1
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        screen.blit(bg_img, [0, 0]) 
        
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        kk_rct.move_ip(sum_mv)

        if check_bound(kk_rct)[0] is False:
            kk_rct.move_ip(-sum_mv[0], 0)
        if check_bound(kk_rct)[1] is False:
            kk_rct.move_ip(0, -sum_mv[1])
        #爆弾サイズと加速度とアタリ判定の更新
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        #加速した実際の速度で移動
        bb_rct.move_ip(avx, avy)

        yoko, tate = check_bound(bb_rct)
        if yoko is False:
            vx *= -1
        if tate is False:
            vy *= -1
       
        if kk_rct.colliderect(bb_rct):
            # ゲームオーバー画面を表示して終了
            gameover(screen)
            return
        
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
