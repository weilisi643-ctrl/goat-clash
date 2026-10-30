# v10.1: semi-alpha pixels left inside v10 fills (were edge, became interior) -> alpha 255, colour kept. _320 via wool_small.
import numpy as np, sys
from scipy import ndimage as nd
sys.argv=['x']; exec(open('/workspace/goat-game/art/_src/director_fix.py').read().split('S={}')[0])
from PIL import Image
ST={}; CURL={'idle':(742,189),'jump':(723,235),'clash':(894,583)}
for pose in ['idle','jump','clash']:
    for w in ['cloud','short']+(['fluffy'] if pose=='clash' else []):
        W=L(f'wool/{w}_{pose}.png'); P=L(f'_v10_pre/wool/{w}_{pose}.png')
        ch=nd.binary_dilation(W[...,3]!=P[...,3],iterations=12)
        inner=nd.binary_erosion(W[...,3]>0,structure=np.ones((3,3)),iterations=7)
        semi=W[...,3]<255; lab,_=nd.label(semi); ext=np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]); ext=ext[ext>0]
        enclosed=semi&~np.isin(lab,ext)                      # v10.1: only semi px fully enclosed by opaque px (outer AA kept)
        y,x=np.ogrid[:1024,:1152]; cx,cy=CURL[pose]; curl=(x-cx)**2+(y-cy)**2<=90**2   # curl hollow + its rim excluded
        z=ch&inner&enclosed&~curl; W[z,3]=255; ST[f'{w}_{pose}']=int(z.sum())
        save(W,f'wool/{w}_{pose}.png',wool_small)
print(ST)
