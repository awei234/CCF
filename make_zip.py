# -*- coding: utf-8 -*-
import zipfile, os
root = r'D:\download\CCF\06_提交物\Prototype'
out = r'D:\download\CCF\06_提交物\Prototype.zip'
if os.path.exists(out):
    os.remove(out)
z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        arc = os.path.join('Prototype', os.path.relpath(p, root))
        z.write(p, arc)
z.close()
print('zip created', out, os.path.getsize(out))
