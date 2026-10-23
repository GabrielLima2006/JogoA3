import sys, glob, os, pygame
pygame.init()
pat, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(pat))
cols = 2; sc = 0.5
w, h = int(960*sc), int(540*sc)
for k in range(0, len(files), 6):
    chunk = files[k:k+6]
    rows = (len(chunk)+cols-1)//cols
    S = pygame.Surface((w*cols, (h+16)*rows)); S.fill((255,255,255))
    f = pygame.font.Font(None, 18)
    for i, fn in enumerate(chunk):
        im = pygame.transform.smoothscale(pygame.image.load(fn), (w, h))
        x, y = (i%cols)*w, (i//cols)*(h+16)
        S.blit(im, (x, y+16)); S.blit(f.render(os.path.basename(fn), True, (0,0,0)), (x+4, y+2))
    pygame.image.save(S, f"{out}_{k//6}.png"); print(f"{out}_{k//6}.png")
