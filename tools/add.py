import json,re,sys
sys.argv=['x']
exec(open('gen.py').read().split("A={}")[0])
A={}
for t in ['Almost! Try again!','Try again!','You can do it! Try again!','Let\'s try together.','Great practice, Noa! You finished the session!']:
    A['p:'+t]=text(t)
print(json.dumps(A)[:80])
open('add.json','w').write(json.dumps(A))
