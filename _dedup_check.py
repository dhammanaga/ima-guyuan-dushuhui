import re,glob,itertools
def bl(f):
    out=[]
    for l in open(f).read().split("\n"):
        s=l.strip()
        if not s: continue
        if s.startswith(('#','-','>','⚠','|','**材料','**《','①','②','③','④')): continue
        if s.startswith('*') or s.startswith('&'): continue
        if s=='[generated, not original text]': continue
        if len(s)>=15 and not re.match(r'^\d+$',s): out.append(s)
    return out
W={}
for f in sorted(glob.glob("读书会14素材/第*周_素材照录.md")):
    n=int(re.search(r'第(\d+)周',f).group(1)); W[n]=bl(f)
for a,b in itertools.combinations(sorted(W),2):
    i=set(W[a])&set(W[b])
    if i: print(f"W{a}∩W{b}: {len(i)}行 例:{list(i)[0][:60]}")
