import re, json, wave, base64, subprocess, numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig
v=PiperVoice.load('/tmp/voice/en-us-lessac-medium.onnx', config_path='/tmp/voice/en-us-lessac-medium.onnx.json')
html=open('/home/claude/noa-english.html').read()
words=re.findall(r"\['([a-z]+)','[A-H]'",html)
rate=v.config.sample_rate
def save(audio,name):
    audio=(audio.astype('float32')/max(1,abs(audio).max())*0.95*32767).astype('int16')
    w=f'/tmp/clips/{name}.wav'
    with wave.open(w,'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(audio.tobytes())
    mp=w[:-4]+'.mp3'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-af','acompressor=threshold=-22dB:ratio=4:attack=5:release=80:makeup=9dB,alimiter=limit=0.97','-ac','1','-ar','22050','-b:a','48k',mp],check=True)
    return 'data:audio/mpeg;base64,'+base64.b64encode(open(mp,'rb').read()).decode()
def text(t,slow=False,name=None):
    cfg=SynthesisConfig(length_scale=2.0 if slow else 1.4)
    chunks=[c.audio_int16_array for c in v.synthesize(t,syn_config=cfg)]
    return save(np.concatenate(chunks),name or re.sub(r'\W','_',t)[:40]+('_s' if slow else ''))
def phon(ph,name,scale=1.3):
    ids=v.phonemes_to_ids(ph)
    a=v.phoneme_ids_to_audio(ids,SynthesisConfig(length_scale=scale))
    if isinstance(a,tuple): a=a[0]
    a=(np.clip(a,-1,1)*32767).astype(np.int16)
    return save(a,name)
A={}
for w in words:
    A['w:'+w]=text(w); A['ws:'+w]=text(w,True)
names={'A':'ay','B':'bee','C':'see','D':'dee','E':'ee','F':'eff','G':'jee','H':'aitch'}
for L,n in names.items(): A['L:'+L]=text(n,name='L'+L)
snd={'A':['ˈ','æ'],'B':['b','ə'],'C':['k','ə'],'D':['d','ə'],'E':['ˈ','ɛ'],'F':['f','ː','ː'],'G':['ɡ','ə'],'H':['h','ə']}
for L,p in snd.items(): A['S:'+L]=phon(p,'S'+L)
phr=['Great job!','Well done!','Amazing!','Super!','Excellent!','You did it!','Wonderful, Noa! Five stars!']
for p in phr: A['p:'+p]=text(p)
for p in ['brush my teeth','eat my breakfast','go to school','do my homework','meet my friends','play on the computer','go to sleep']:
    A['d:'+p]=text('Every day I '+p)
for q in ["What's your name?",'How are you?','What animal do you like?','What color are your eyes?','What is your favorite food?','What is your favorite sport?']:
    A['q:'+q]=text(q)
for a in ['My name is Noa.',"I'm fine, thank you!",'I like unicorns!','My eyes are brown','My favorite food is pizza.','My favorite sport is swimming.']:
    A['a:'+a]=text(a); A['as:'+a]=text(a,True)
open('/home/claude/gen/audio.js','w').write('const AUDIO='+json.dumps(A)+';')
print(len(A), sum(len(x) for x in A.values())//1024,'KB')
