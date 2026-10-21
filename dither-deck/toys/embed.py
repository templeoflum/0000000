import re, sys, time
time.sleep(0.5)
deck_path, toy_path, ph, which = sys.argv[1:5]
deck = open(deck_path).read()
mask = re.search(which + r'="([^"]+)"', deck).group(1)
s = open(toy_path).read()
assert ph in s, "placeholder missing in " + toy_path
s = s.replace(ph, mask)
open(toy_path, "w").write(s)
print(which, "embedded into", toy_path, "KB:", len(s)//1024)
