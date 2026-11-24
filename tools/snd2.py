import numpy as np, wave, subprocess, base64, json
from piper import PiperVoice
from piper.config import SynthesisConfig
v=PiperVoice.load('/tmp/voice/en-us-lessac-medium.onnx', config_path='/tmp/voice/en-us-lessac-medium.onnx.json')
sr=v.config.sample_rate; fr=int(sr*0.01)
def synth(t,ls=1.3): return np.concatenate([c.audio_float_array for c in v.synthesize(t,syn_config=SynthesisConfig(length_scale=ls))])
def feats(a):
    n=len(a)//fr
    rms=np.array([np.sqrt(np.mean(a[i*fr:(i+1)*fr]**2)) for i in range(n)])
    zcr=np.array([np.mean(np.abs(np.diff(np.sign(a[i*fr:(i+1)*fr])))>0) for i in range(n)])
    return rms,zcr,n
def fade(seg,fi=0.01,fo=0.04):
    seg=seg.copy(); a=int(sr*fi); b=int(sr*fo)
    if len(seg)>a: seg[:a]*=np.linspace(0,1,a)
    if len(seg)>b: seg[-b:]*=np.linspace(1,0,b)
    return seg
def norm(seg): return seg/(np.abs(seg).max()+1e-9)*0.9
def loop(seg,target):
    # lengthen a steady sound by crossfading copies of its middle
    if len(seg)>=target: return seg[:target]
    cf=int(sr*0.015)
    if len(seg)<int(sr*0.08): seg=np.concatenate([seg]*4)
    mid=seg[len(seg)//4:3*len(seg)//4]
    if len(mid)<=2*cf: return seg
    out=seg[:len(seg)//4].copy(); out=seg[:len(seg)//4].copy()
    while len(out)<target-len(seg)//4:
        m=mid.copy()
        if len(out)>cf:
            out[-cf:]=out[-cf:]*np.linspace(1,0,cf)+m[:cf]*np.linspace(0,1,cf); m=m[cf:]
        out=np.concatenate([out,m])
    return np.concatenate([out,seg[3*len(seg)//4:]])
info={}
def vowel(w):
    a=synth(w,1.4); r,z,n=feats(a); mx=r.max(); s=int(np.argmax(r>0.04*mx)); pk=s+int(np.argmax(r[s:]))
    e=pk
    while e<n and r[e]>0.15*mx: e+=1
    e=min(e,s+30); return fade(a[s*fr:e*fr]),(s,e)
def tail(w,kind,ls=2.4):
    for _ in range(6):
        seg,inf=_tail(w,kind,ls)
        if len(seg)>int(sr*0.3): return seg,inf
    return seg,inf
def _tail(w,kind,ls=2.4):
    a=synth(w,ls); r,z,n=feats(a); mx=r.max(); act=[i for i in range(n) if r[i]>0.006*mx]; end=act[-1]+1
    pk=int(np.argmax(r))
    if kind=='fric':   # noisy frames at the end
        s=end
        while s-1>pk and z[s-1]>0.18: s-=1
    else:              # nasal / l / r: weaker voiced tail after the vowel peak
        s=pk
        while s<end and r[s]>0.55*mx: s+=1
    seg=a[s*fr:end*fr]
    if len(seg)<int(sr*0.05): return seg,(s,end)
    return fade(loop(seg,int(sr*0.75)),0.03,0.08),(s,end)
def onset(w,kind,ms):
    a=synth(w,1.3); r,z,n=feats(a); mx=r.max(); s=int(np.argmax(r>0.012*mx))
    if kind=='voiceless':  # until voicing starts
        e=s+2
        while e<n and not (z[e]<0.15 and r[e]>0.2*mx): e+=1
        e=min(e+2,s+ms//10)
    else: e=s+ms//10
    return fade(a[s*fr:e*fr],0.003,0.03),(s,e)
def rep3(seg):
    gap=np.zeros(int(sr*0.35)); return np.concatenate([seg,gap,seg,gap,seg])
S={}
for L,w in {'A':'at','E':'etch','I':'it','O':'ox','U':'up'}.items(): seg,info[L]=vowel(w); S[L]=rep3(norm(seg))
for L,(w,k) in {'F':('off','fric'),'S':('miss','fric'),'Z':('buzz','fric'),'V':('love','fric'),'M':('hum','n'),'N':('sun','n'),'L':('bell','n'),'R':('fur','n')}.items():
    seg,info[L]=tail(w,k); S[L]=norm(seg)
for L,(w,k,ms) in {'B':('bat','v',60),'C':('cat','voiceless',120),'K':('kit','voiceless',120),'D':('dog','v',60),'G':('gap','v',60),'H':('hat','voiceless',180),
                   'J':('jam','v',110),'P':('pat','voiceless',120),'T':('tap','voiceless',120),'W':('wet','v',120),'Y':('yes','v',110),'Q':('queen','voiceless',170)}.items():
    seg,info[L]=onset(w,k,ms); S[L]=rep3(norm(seg))
# X = "ks" at the end of "box"
a=synth('box',1.6); r,z,n=feats(a); mx=r.max(); act=[i for i in range(n) if r[i]>0.006*mx]; end=act[-1]+1
pk=int(np.argmax(r)); s=pk
while s<end and r[s]>0.06*mx: s+=1    # vowel + k closure
s=max(pk+3,s-3); end=min(end,s+28); info['X']=(s,end); S['X']=rep3(norm(fade(a[s*fr:end*fr],0.005,0.04)))
out={}
for L,seg in S.items():
    seg=np.concatenate([np.zeros(int(sr*.04)),seg,np.zeros(int(sr*.06))])
    w16=(np.clip(seg,-1,1)*32767).astype(np.int16); fn=f'/tmp/clips/P{L}'
    with wave.open(fn+'.wav','wb') as wf: wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr);wf.writeframes(w16.tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',fn+'.wav','-af','acompressor=threshold=-22dB:ratio=3:attack=5:release=80:makeup=7dB,alimiter=limit=0.97','-ac','1','-ar','22050','-b:a','48k',fn+'.mp3'],check=True)
    out['S:'+L]='data:audio/mpeg;base64,'+base64.b64encode(open(fn+'.mp3','rb').read()).decode()
    print(L, info[L], 'ms', int(len(seg)/sr*1000))
json.dump(out,open('snd2.json','w'))
