#####check urllib is good
def runexit(newestResultId):
    if newestResultId != None:
        with open("mostRecentListingID_eb.txt", 'w') as f:
            f.write(newestResultId)
            print("wrote newest ID. looked at all newest posts.")
def findLine(pt1, pt2):
    m = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
    b = pt2[1] - m * pt2[0]
    return m, b
def prep():
    print("running prep")
    import re
    import requests
    from bs4 import BeautifulSoup as bs
    #CraigslistHousing.show_filters()

    #init slack
    from slackclient import SlackClient
    print("imports done")
    SLACK_TOKEN = "None"
    with open("token_eb.txt") as f:
        SLACK_TOKEN = f.readline().strip()
    SLACK_CHANNEL = "#housing"
    SLACK_CHANNEL_repeat = "#repeats"
    sc = SlackClient(SLACK_TOKEN)
    print("slack prepped")
    
    args = [sc, "holder", SLACK_TOKEN, SLACK_CHANNEL, SLACK_CHANNEL_repeat,"lastId",
        "ids",requests,bs,re]
    return args

# def testFn():
#     from craigslist import CraigslistHousing
#     cl = CraigslistHousing(site='boston', area='gbs', category='aap',
#                              filters={'max_price': 2400, 'min_price': 1600, 'max_bedrooms': 2,
#                                       'min_bedrooms': 1, 'bundle_duplicates':True})
#     results = cl.get_results(sort_by='newest', geotagged=True, limit=200)
#     for result in results:
#         print(result['id'])
#         break
'''
To implement:
remove fenway?
removes: "raymond ng","randy horn": implemented
improved dating: implemented

'''





def do_scrape(args):
    newFileName = "allGoodListingIDsAndNames_withPriceAndDate_eb.txt"
    print("running")
    sc = args[0]
    import time
    #CraigslistHousing = args[1]
    SLACK_TOKEN = args[2]
    SLACK_CHANNEL = args[3]
    SLACK_CHANNEL_repeat = args[4]
    #lastId = args[5]
    #ids = args[6]
    requests = args[7]
    bs = args[8]
    re = args[9]
    with open("mostRecentListingID_eb.txt",'r') as f:
        lastId = str(f.read().strip())
    newestResultId = lastId
    ids = {}
    #with open("allGoodListingIDsAndNames.txt",'r') as f:
        #for line in f:
        #    ids.add(str(line.strip()))
    with open(newFileName,'r') as f:
        for line in f:
            try:
                splitline = line.strip().split("{}")
                ids[splitline[0]] = [splitline[2],splitline[3]] #ID: price, date
                ids[splitline[1]] = [splitline[2],splitline[3]] #name: price, date
            except Exception as e:
                pass
    
    print("loaded files")


    from craigslist import CraigslistHousing
    # print("here")
    cl = CraigslistHousing(site='boston', area='gbs', category='aap',
                             filters={'max_price': 2501, 'min_price': 1600, 'max_bedrooms': 2,
                                      'min_bedrooms': 1, 'bundle_duplicates':True})
    

    # print("here")
    results = cl.get_results(sort_by='newest', geotagged=True, limit=1000)

    print("cl prepped")

    #define region
    misHil = (42.328017, -71.111547)
    fen = (42.342610,-71.09433)
    beaconEast = (42.348129, -71.100733)
    beaconWest = (42.343926, -71.127147)
    pondSouth = (42.327430, -71.119658)

    #t-stops
    chestNutHill = (42.326864,-71.164454)
    reservoir = (42.334995,-71.148695)
    beaconsfield = (42.335706,-71.140379)
    brooklineHills = (42.331315,-71.126631)

    #define lines
    pointPairs = [[misHil, fen, 'pos'],[fen, beaconEast, 'pos'], #
                  [beaconWest, pondSouth, 'neg'],[beaconEast, beaconWest, 'neg'],[pondSouth, misHil, 'pos']]

    circleCenters = [brooklineHills,beaconsfield,reservoir,chestNutHill]
    #pos, neg is intuitive, if above then good (unsure for vert/horizontal
    lineFilters = []
    for pair in pointPairs:
        slope, intercept = findLine(pair[0], pair[1])
        lineFilters.append([slope, intercept, pair[2]])

    #regexDateApril = re.compile(r'4.1')
    #regexDateMay = re.compile(r'5.1')

    goodCount = 0
    repostCount = 0
    totalCount = 0
    goodDates = 0
    newestResultId = None
    print("searching")
    for result in results:
        result['name'] = ''.join([i if ord(i) < 128 else ' ' for i in result['name']])
        #wtf slow downnnnn
        time.sleep(1)
        #print(result['id'])
        #prep, pre-checks
        if totalCount % 1 ==0:
            print(totalCount)
        repeat=False
        if result['id'] == lastId:############################
            break
        flags = ""
        totalCount += 1
        if newestResultId == None:
            newestResultId = result['id']
        # filter
        try:
            kitchenFlag = False
            if "studio" in result['name'].lower():
                continue
            if "kitchen" in result['name'].lower() or "granite" in result['name'].lower() or "open" in result['name'].lower():
                kitchenFlag = True
            #if re.search('4/|-1',result['name'].lower()) or re.search('5/|-1',result['name'].lower()) or \
            #                'april' in result['name'].lower() or 'may' in result['name'].lower():
            #    flags += "-BEWARE early date-"
            bad = True
            if result["geotag"] != None:
                a, b = result["geotag"]
                bad = False
                for line in lineFilters:
                    calcVal = a*line[0] + line[1] - b
                    if (calcVal < 0 and line[2] == "pos") or (calcVal > 0 and line[2] == "neg"):
                        bad = True
                        #print(line)
                        break
                if bad:
                    for tcenter in circleCenters:
                        if ((a-tcenter[0])**2 + (b-tcenter[1])**2) < 4.742e-5: #12 minute map direct walk
                            #near a T stop, so its ok!
                            #bad = False
                            flags += "-near T-"
                            #print((a,b))
                            #print((a-tcenter[0])**2 + (b-tcenter[1])**2)
            else:
                if result["where"] == None:
                    flags += "-no location-"
                    bad = False
                elif ("brookline" in result["where"].lower() or #"brighton" in result["where"].lower() or
                      "longwood" in result["where"].lower() or
                      "coolidge" in result["where"].lower()):
                    flags +="-no geotag-"
                    bad = False
                else:
                    continue
            if not bad:
                thisUrl = result['url']
                #print(thisUrl)
                request = requests.get(thisUrl)
                soup = bs(request.content, 'html.parser')
                #page = urlopen(thisUrl)
                #soup = bs(page, 'html.parser')
                print(soup)
                moveDate = soup.find('span', attrs={'class': "housing_movein_now property_date shared-line-bubble"})
                mainText = soup.find('section', attrs={'id': "postingbody"}).text
                title = soup.find("span", attrs={'id':"titletextonly"}).text

                if moveDate != None:
                    splitDate = moveDate.text.strip().split(' ')
                    date = ' '.join(splitDate[1:])
                else:
                    dates = ["0?1|jan","0?2|feb","0?3|mar","0?4|apr","0?5|may","0?6|jun","0?7|jul","0?8|aug","0?9|sep","10|oct","11|nov","12|dec","NOW|now"]
                    splitDate = []
                    for thisDate in dates:
                        if len(re.compile("avail(able)?( date)?:? (%s)" % thisDate).findall(mainText.lower())) > 0:
                            date = thisDate.split("|")[1]
                            splitDate = [date,date]
                        if len(re.compile("avail(able)?( date)?:? (%s)" % thisDate).findall(title.lower())) > 0:
                            date = thisDate.split("|")[1]
                            splitDate = [date,date]
                    if len(splitDate) == 0:
                        date = "dnf"
                        splitDate = ["dnf","dnf"]
                badKeywords = ["raymond ng","randy horn"]
                for keyword in badKeywords:
                    if keyword in mainText.lower():
                        print("%s in mainText. skipping." % keyword)
                        bad = True
                if bad:
                    continue

                laundryInUnit = False
                laundry1 = soup.find_all('p', attrs={'class': "attrgroup"})
                for i in laundry1:
                    for string in i.strings:
                        if "w/d in unit" in string:
                            print("halleloughsoeursjgn")
                            laundryInUnit = True
                            flags = "--w/d in unit--" + flags
                            break
                flags = "*" + date + "*" + flags
                notRepeat = True
                print(result)
                for item in ['id','name']:
                    if result[item] in ids:
                        repostCount += 1
                        flags = "-repeat-" + flags
                        different = False
                        if result["price"] != ids[result[item]][0]:
                            different = True
                            flags = "-cheaperBy $%s-" % (int(ids[result[item]][0].split("$")[1]) - int(result["price"].split("$")[1])) + flags
                            ids[result[item]] = [result["price"], date]
                        if date != ids[result[item]][1]:
                            different = True
                            flags = "-dateChange-" + flags
                            ids[result[item]] = [result["price"], date]
                        notRepeat = notRepeat and different
                    else:
                        ids[result[item]] = [result["price"], date]
                # if notRepeat:
                # desc = "{0} {1} | {2} | {3} | <{4}>".format(flags, result["price"], result["name"], result["geotag"], result["url"])
                # response = sc.api_call(
                #     "chat.postMessage", channel=SLACK_CHANNEL, text=desc,
                #     username='pybot', icon_emoji=':robot_face:')
                print("not repeat?")
                print(notRepeat)
                if notRepeat:
                    goodCount += 1
                    with open(newFileName, 'a') as f:
                        try:
                            f.write("%s{}%s{}%s{}%s\n" % (result['id'],result['name'],result['price'],date ))
                        except Exception as e:
                            try:
                                f.write("%s{}%s{}%s{}%s\n" % (result['id'],"nullName",result['price'],date ))
                            except Exception as e:
                                    print(e)
                                    print("error writing")
                                    continue
                            pass
                    desc = "{0} {1} | {2} | {3} | <{4}>".format(flags, result["price"], result["name"], result["geotag"], result["url"])
                    response = sc.api_call(
                        "chat.postMessage", channel=SLACK_CHANNEL, text=desc,
                        username='pybot', icon_emoji=':robot_face:')
                    #if (splitDate[1] == "jul") or (splitDate[1] == "jun" and int(splitDate[2]) > 1):
                    #    goodDates += 1
                    #    sc.api_call("reactions.add",channel=str(response['channel']),timestamp=str(response['ts']),name="star")
                    if (splitDate[1] == "jul") or (splitDate[1] == "jun") or (splitDate[1] == "may") or (splitDate[1] == "apr"):
                        goodDates += 1
                        sc.api_call("reactions.add",channel=str(response['channel']),timestamp=str(response['ts']),name="star")
                    if laundryInUnit:
                        sc.api_call("reactions.add",channel=str(response['channel']),timestamp=str(response['ts']),name="blond-haired-woman")
                
                else:
                    desc = "{0} {1} | {2} | {3} | <{4}>".format(flags, result["price"], result["name"], result["geotag"], result["url"])
                    repostCount += 1
                    sc.api_call(
                        "chat.postMessage", channel=SLACK_CHANNEL_repeat, text=desc,
                        username='pybot', icon_emoji=':robot_face:')
                    #####################################################################end changes
            else:
                pass
        except NameError as e:
            print("here...?")
            if "not a valid area" in e:
                print("awwww f***")
                sc.api_call("chat.postMessage",channel="#logging", text="Likely IP ban.",username='pybot', icon_emoji=':robot_face:')
                break
            print(e)
            continue

    outmessage = "scraped %s new posts; found %s good posts, %s reposts, and %s that match our dates!" % (totalCount, goodCount, repostCount, goodDates)
    sc.api_call("chat.postMessage",channel="#logging", text=outmessage,username='pybot', icon_emoji=':robot_face:')
    print(outmessage)
    with open("clLog.txt", 'a') as f:
        f.write(outmessage + "\n")
    runexit(newestResultId)
    return totalCount
#a = prep()
#do_scrape(a)
