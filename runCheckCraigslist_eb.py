import time
import sys
import traceback

sys.path.insert(0,"/home/unix/ebartell/craigslist/pylibs/lib/python3.6/site-packages/")
from threading import Thread
import functools

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

if __name__ == "__main__":
    print(sys.path)
    from checkCraigslist_eb import *
    prepOutput = prep()
    #print(prepOutput)
    #exit()
    while True:
        print("{}: Starting scrape cycle".format(time.ctime()))
        lastCount = 0
        out="temp"
        try:
            from checkCraigslist_eb import do_scrape
            func = timeout(timeout=30*60)(do_scrape)
            out = func(prepOutput)
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            if "not a valid area" in str(exc):
                print("awwww f***")
                break
            if "timeout" in str(exc):
                print("timeout, rerunning")
                continue
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
            continue
        else:
            print("{}: Successfully finished scraping".format(time.ctime()))
            try:
                lastCount += out
            except Exception as e:
                pass
        minutesToWait = int(max(15 - lastCount/20,8))
        for minute in range(minutesToWait):
        	print("%s minutes until next scrape" % (minutesToWait - minute))
        	time.sleep(1*60)














