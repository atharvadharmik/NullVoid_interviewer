
# Driver function
import os
if __name__ == "__main__":
    for (root,dirs,files) in os.walk('.', topdown=True):
        for file in files:
            print (file)
        print ('--------------------------------')