from PIL import Image, ImageChops
import numpy as np
A='/workspace/goat-game/art/'
def tint(path,color,div):
    im=np.array(Image.open(path).convert('RGBA')).astype(float)
    g=im[...,:3].mean(-1,keepdims=True)
    im[...,:3]=np.clip(g/div*np.array(color),0,255)
    return Image.fromarray(im.astype('uint8'))
def goat(pose,wool,horn,wc,hc,out,flip=False):
    c=tint(A+f'wool/{wool}_{pose}.png',wc,255)
    import os
    k=A+f'wool/knee_{pose}.png'
    for p in [k,A+f'body/body_{pose}.png',A+f'beard/beard_{pose}.png',A+f'face/face_{pose}.png']:
        if os.path.exists(p): c.alpha_composite(Image.open(p).convert('RGBA'))
    c.alpha_composite(tint(A+f'horn/{horn}_{pose}.png',hc,128))
    c=c.crop(c.getbbox())
    if flip: c=c.transpose(Image.FLIP_LEFT_RIGHT)
    c.save(out)
goat('idle','fluffy','curl',(250,248,242),(214,182,120),'g_home.png')
goat('idle','fluffy','curl',(250,248,242),(214,182,120),'g_me.png')
goat('idle','short','straight',(120,112,104),(200,190,170),'g_op.png',True)
