import time
import hashlib

def md5_(key):
    md5 = hashlib.md5()
    md5.update(key.encode())
    return md5.hexdigest()

t = int(time.time())
i = hex(t).replace("0x",'').upper()
e = str(md5_(str(t))).replace("0x",'').upper()

s = e[0:5]
o = e[-5:]
n = ''
l = ''
for x in range(5):
    n += s[x] + o[x]
for j in range(5):
    l += i[j + 3] + o[j]
as_ = 'A1' + n + i[-3:]
cp = i[:3] + l + 'E1'
print(t)
print(as_)
print(cp)
'''
A1B5E9E921F8F81
A10519D90178F
'''
'''
      for (var s = e.slice(0, 5), o = e.slice(-5), n = "", a = 0; 5 > a; a++)
            n += s[a] + i[a];
        for (var l = "", r = 0; 5 > r; r++)
            l += i[r + 3] + o[r];
        return {
            as: "A1" + n + i.slice(-3),
            cp: i.slice(0, 3) + l + "E1"
        }

'''
