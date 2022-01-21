class Res:

    def get(url,file):
        try:
            response = get('https://marty5499.github.io/pythonCode/'+url)
            print(">>",len(response.text) )
            print("get file:",file,'size:',len(response.text),',save to:',file)
            f = open(file, 'w')
            f.write(response.text)
            f.close()
            print("OK.")
        except Exception as e:
            print("QQ:",e)


    def exe(dir):
        srcDir = dir
        try:
            while True:
                idx = dir.index('/')
                try:
                    name = dir[0:idx]
                    try:
                        print('mkdir',name)
                        os.mkdir(name)
                    except:
                        pass
                    try:
                        os.chdir(name)
                        print('cd',name)
                    except:
                        pass
                except:
                    pass
                dir = dir[idx+1:]
        except:
            pos = -1
            try:
                pos = dir.index('.mpy')
            except:
                pass
            try:
                if pos == -1:
                    pos = dir.index('.py')
            except:
                pass
            try:
                if pos > 0:
                    pyFile = dir
                    Res.get(srcDir,pyFile)
                else:
                    try:
                        print("mkdir",dir)
                        os.mkdir(dir)
                    except:
                        pass
                    try:
                        os.chdir(dir)
                        print("cd ",dir)
                    except:
                        pass
            except:
                pass
        os.chdir('/')