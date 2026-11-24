import json
exec(open('gen.py').read().split("A={}")[0])
A={}
words=['ant','cat','guitar','insect','juice','kite','lion','moon','nose','octopus','pig','queen','rabbit','sun','tiger','umbrella','van','watch','box','yo-yo','zebra','red','blue','yellow','green','orange','purple','pink','black','white','brown']
for w in words:
    A['w:'+w]=text(w); A['ws:'+w]=text(w,True)
for t in ['My eyes are blue.']:
    A['a:'+t]=text(t); A['as:'+t]=text(t,True)
for t in ['Your turn! Say it.','Listen.','What color is it?','Repeat after me.']:
    A['p:'+t]=text(t)
names={'I':'eye','J':'jay','K':'kay','L':'ell','M':'em','N':'en','O':'oh','P':'pee','Q':'cue','R':'are','S':'ess','T':'tee','U':'you','V':'vee','W':'double you','X':'ex','Y':'why','Z':'zee'}
for L,n in names.items(): A['L:'+L]=text(n,name='L'+L)
json.dump(A,open('gen2.json','w')); print(len(A))
