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

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー、その方向に応じたこうかとん画像Surfaceを値とした辞書を生成する。

    引数:
        なし

    戻り値:
        dict[tuple[int, int], pg.Surface]: 移動量 (vx, vy) に対するこうかとん画像Surfaceの辞書
    """
    # ベースとなるこうかとん画像（右向きにするためにまずはflipするのが一般的です）
    # 元の画像（3.png）は左を向いているので、左右反転させて右向きの基準画像を作ります
    base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img_r = pg.transform.flip(base_img, True, False)
    img_l = base_img                                

    # 各方向の移動量タプルに対応する回転画像を辞書に登録
    kk_dict = {
        (0, 0):   img_l,                                       
        (+5, 0):  img_r,                                       
        (+5, -5): pg.transform.rotozoom(img_r, 45, 1.0),       
        (0, -5):  pg.transform.rotozoom(img_r, 90, 1.0),       
        (-5, -5): pg.transform.rotozoom(img_l, -45, 1.0),      
        (-5, 0):  img_l,                                       
        (-5, +5): pg.transform.rotozoom(img_l, 45, 1.0),       
        (0, +5):  pg.transform.rotozoom(img_l, -90, 1.0),      
        (+5, +5): pg.transform.rotozoom(img_r, -45, 1.0),      
    }
    
    return kk_dict

def activate_frenzy_mode(screen: pg.Surface, kk_rct: pg.Rect, bb_rct: pg.Rect) -> tuple[int, int]:
    """
    10秒経過後に発動する「血迷いモード」。背景を紫色に変更し、
    こうかとんが爆弾を自動追尾するための移動量を計算して返す。

    引数:
        screen (pg.Surface): 描画対象のメイン画面Surface
        kk_rct (pg.Rect): こうかとんのRectオブジェクト
        bb_rct (pg.Rect): 爆弾のRectオブジェクト

    戻り値:
        tuple[int, int]: 爆弾を追尾するためのこうかとんの移動量 (vx, vy)
    """
    # 1. 背景を紫（赤と青を混ぜた色：128, 0, 128 など）で塗りつぶす
    screen.fill((128, 0, 128))
    
    # 2. こうかとんから見た爆弾の方向（ベクトル）を計算
    # 爆弾の座標 - こうかとんの座標
    dx = bb_rct.centerx - kk_rct.centerx
    dy = bb_rct.centery - kk_rct.centery
    
    # 3. 追尾する速度を設定（今回は少し速めの速度 4 に調整）
    # 方向に応じて移動量を +4, -4, 0 に振り分ける
    kk_vx = 4 if dx > 0 else (-4 if dx < 0 else 0)
    kk_vy = 4 if dy > 0 else (-4 if dy < 0 else 0)
    
    return kk_vx, kk_vy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    # 8方向のこうかとん画像辞書を取得
    kk_imgs = get_kk_imgs()
    # 初期画像として静止時(0, 0)の画像を設定
    kk_img = kk_imgs[(0, 0)]
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
        # 合計移動量をタプルにして辞書から対応する画像を抽出
        kk_img = kk_imgs[tuple(sum_mv)]
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
