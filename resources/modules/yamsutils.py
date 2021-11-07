import hashlib
import os
from functools import reduce

def __digest( directory ):
    hash = []
    for root, dirs, files in os.walk(directory):
        for names in files:
            if not names.endswith( '.py' ):
                continue
            filepath = os.path.join(root,names)
            try:
                f1 = open(filepath, 'rb')
            except:
                # You can't open the file for some reason
                f1.close()
                continue
            hash.append( (names, hashlib.sha256(f1.read()).hexdigest() ) )

    hash.sort( key=lambda tup: tup[ 1 ])
    # digest = reduce( lambda d, (x,y): d + '\n' + y, hash, '')
    digest = reduce( lambda d, xy: d + '\n' + xy[1], hash, '')

    return hashlib.sha256(digest[1:].strip().encode('utf-8')).hexdigest()

if __name__ == '__main__':
    print(( __digest( '.' )))
