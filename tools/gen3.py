import json
exec(open('gen.py').read().split("A={}")[0])
A={}
words=['igloo','ice cream','armchair','bookcase','bed','chair','cupboard','closet','desk','fridge','ear','cheeks','back','chin','hand','feet','hair','arm','finger','elbow']
for w in words: A['w:'+w]=text(w); A['ws:'+w]=text(w,True)
for w in ['ear','cheeks','chin','hand','eye','foot','feet','hair','arm','finger','elbow']: A['t:'+w]=text('Touch the '+w+'!')
A['q:What do you like to eat?']=text('What do you like to eat?')
A['a:I like pizza.']=text('I like pizza.'); A['as:I like pizza.']=text('I like pizza.',True)
json.dump(A,open('gen3.json','w')); print(len(A))
