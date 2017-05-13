from bottle import static_file,route, run, template, get , post , request
from tweepy import API,Cursor,TweepError

import geocoder
geoC = geocoder.Geocoder(dataset='geonames')

#Import the necessary methods from tweepy library
from tweepy import OAuthHandler
from tweepy import API
from tweepy import TweepError
#import json
import langid

import pickle
import cPickle
import numpy as np

import gcd_dist
import lib_grid_search
import re
from haversine import haversine

from nltk.tokenize import TweetTokenizer
tknzr = TweetTokenizer()

def distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)

    return haversine(point1, point2)



def catch_account(accountName):
    global api
    access_token = "2784918864-O8cwCRjgyWXUZElzRGFEY1c1NM3Pt0RJGIoOiIF"
    access_token_secret = "w1hRSA7n6cccSHOzCACIo47ALptky3GB3HFvkMelvWysS"
    consumer_key = "iLH7y24uarb88u9Vq5EN9Dm5d"
    consumer_secret = "71FCC5qpvyWuJhzAHXtghXa9jlfOffeFGahby6YyzX1gPiuJS3"

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = API(auth)
    stuff = api.user_timeline(screen_name =accountName, count = 100, include_rts = True)
    followers = api.followers(accountName)
    #print 'followers'
    #print [f.screen_name for f in followers if api.lookup_friendships(accountName,f.screen_name)]
    print len(stuff)
    text = ''
    mentions = []
    locations =[]

    followID = []
    for friend in Cursor(api.friends, screen_name=accountName,count = 10).items():
        relation = api.show_friendship(source_screen_name=accountName, target_screen_name=friend.screen_name)
        if relation[0].followed_by:
            followID.append(friend.screen_name)
        
    print followID


    
    for status in stuff:
        # combine all text
        text+=(status.text+' ')

        # check location status of tweets
        location = status.coordinates
        if location:
            loc = location['coordinates'][::-1]
            locations.append(loc)
        elif status.user.location:
            #locations.append(geoC.geocode_noisy(status.user.location)) #its the name not the geo. Its fixed now!
            locations = [geoC.geocode_noisy(status.user.location)] #its the name not the geo. Its fixed now!
        elif status.user.time_zone:
            #locations.append(geoC.geocode_noisy(status.user.time_zone)) #its the name not the geo. its fixed now!
            locations = [geoC.geocode_noisy(status.user.time_zone)] #its the name not the geo. its fixed now!
        # Mentions in tweets
        smentions = status.entities['user_mentions']
        for s in smentions:
            if s!=[] and s['screen_name'].lower()!=accountName.lower():
                mentions.append(s['screen_name'].lower())
        
    return text,locations,mentions

def mentions_loc(mentions):
        locations = {}
        for m in mentions:
            try:
                stuff_s = api.user_timeline(screen_name =m, count = 1, include_rts = True)
                if stuff_s:
                    
                    if stuff_s[0].user.location and geoC.geocode_noisy(stuff_s[0].user.location):
#                        print stuff_s[0].user.location
                        (lat,lon) = geoC.geocode_noisy(stuff_s[0].user.location)
                        location = geoC.reverse_geocode(lat,lon)
                        locations[location] = locations.get(location,0)+1
                    elif stuff_s[0].user.time_zone and geoC.geocode_noisy(stuff_s[0].user.time_zone):
                        (lat,lon) = geoC.geocode_noisy(stuff_s[0].user.time_zone)
                        location = geoC.reverse_geocode(lat,lon)
                        locations[location] = locations.get(location,0)+1
            except TweepError:
                print 'protected account'        
        locations =  {l:locations[l] for l in locations if locations[l]>1}
        locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]    
        return [l[0].replace('\t',' ')[:-3].title()+', '+l[0].replace('\t',' ')[-2:].upper()+' '+str(l[1]) for l in locations]
def catch_mention_account(accountName):
    global api
    print accountName
    try:
        stuff = api.user_timeline(screen_name =accountName, count = 100, include_rts = True)
    except TweepError:
        print("Failed to run the command on that user, Skipping...")
        return [],[]
    locations = []
    mentions = []
    
    for status in stuff:
            
            location = status.coordinates
            smentions = status.entities['user_mentions']
            for s in smentions:
                if s!=[]:
                    mentions.append(s['screen_name'])
            #print status.user.time_zone
            if location:
                locations.append(location['coordinates'][::-1])
                #print locations
                loc = location['coordinates'][::-1]
                city = lib_grid_search.zoom_search(loc[0],loc[1])
                return city,[]
            
    #print locations
    return [],set(mentions)


def follow_loc(mentions):
        locations = {}
        for m in mentions:
            try:
                stuff_s = api.user_timeline(screen_name =m, count = 1, include_rts = True)
                if stuff_s:
                    
                    if stuff_s[0].user.location and geoC.geocode_noisy(stuff_s[0].user.location):
#                        print stuff_s[0].user.location
                        (lat,lon) = geoC.geocode_noisy(stuff_s[0].user.location)
                        location = geoC.reverse_geocode(lat,lon)
                        locations[location] = locations.get(location,0)+1
                    elif stuff_s[0].user.time_zone and geoC.geocode_noisy(stuff_s[0].user.time_zone):
                        (lat,lon) = geoC.geocode_noisy(stuff_s[0].user.time_zone)
                        location = geoC.reverse_geocode(lat,lon)
                        locations[location] = locations.get(location,0)+1
            except TweepError:
                print 'protected account'        
        locations =  {l:locations[l] for l in locations if locations[l]>1}
        locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]    
        return [l[0].replace('\t',' ')[:-3].title()+', '+l[0].replace('\t',' ')[-2:].upper()+' '+str(l[1]) for l in locations]


def geolocate(text):
    global vectorizer,clf, classLatMedian, classLonMedian
    text = re.sub(r"(?:\@|https?\://)\S+", "", text)
    #text = "here is melbourne and sydney"
    X_test = [text]
    X_test = vectorizer.transform(X_test)
    features = vectorizer.get_feature_names()
    print 'weights:'
    
    
    
    preds = [clf.predict(X_test)[0]]
    weights = [1]
    print preds[0]
    print clf.coef_[preds[0]]
    print np.array(clf.coef_[preds[0]]).shape
    
    prediction = categories[preds[0]]
    medLat = [classLatMedian[prediction]]
    medLon = [classLonMedian[prediction]]

    city = lib_grid_search.zoom_search(medLat[0],medLon[0])
    #    print cc2_bah
     
    probs = clf.predict_proba(X_test)[0]
    preds = probs.argsort()[:-7:-1]

#    probs = clf.predict_proba(X_test)[0]
#    print probs.argmax()
#    print max(probs)
#    #print probs[-10:]
#    print probs.argsort()[-10:]
#    preds = probs.argsort()[:-10:-1]
#    print preds
    X_test = X_test.toarray()[0]
    print X_test
    print type(X_test)
    print type(X_test[0])
    print X_test.shape
    print 'multiplication:'
    X_test = np.array(X_test) * np.array(clf.coef_[preds[0]])
    print X_test
    print X_test.shape
    print sum(X_test)
    indexes = X_test.nonzero()
    print type(indexes)
    #print indexes.toarray()
    #indexes = indexes.toarray()
    print indexes
    #indexes = indexes[0].toarray()
    frEnt = open('entropy-scores.txt','r')
    #for i in indexes:
    #    print i,
    #    print X_test[i],
    #    print features[i]
    #feats = tknzr.tokenize(text)
    feats = {features[i]:X_test[i] for i in indexes[0]}
    ent = {}
    for line in frEnt:
            tokens = line.strip().split()
            ent[tokens[0]] = float(tokens[1])
    frEnt.close()
    entropyW = {w:ent[w] for w in feats if w in ent}
    #print 'entropy:'
    entropyW = sorted(entropyW.items(), key=lambda x: x[1])[:10]    
    #print entropyW


    frKL = open('KL-scores.txt','r')
    KL = {}
    for line in frKL:
            tokens = line.strip().split()
            KL[tokens[0]] = float(tokens[1])
    frKL.close()
    KLW = {w:KL[w] for w in feats if w in KL}
    #print 'entropy:'
    KLW = sorted(KLW.items(), key=lambda x: x[1], reverse=True)[:10]    




    #print 'feature weights:'
    #feats = {features[i]:X_test[0,i] for i in indexes}
    feats = sorted(feats.items(), key=lambda x: x[1],reverse = True)[:10]
    #print feats

    
    medLons = []
    medLats = []
    weights = []
    cities = []
    for i in range(1, len(preds)):
        prediction = categories[preds[i]]
        medLats.append(classLatMedian[prediction])
        medLons.append(classLonMedian[prediction])
        cc2_bah = lib_grid_search.zoom_search(classLatMedian[prediction],classLonMedian[prediction])
        if cc2_bah[0]==None:
            continue
        cc2_bah = cc2_bah[0].split('-')
        cc2_bah = cc2_bah[0].title()+', '+cc2_bah[2].upper()
        #print cc2_bah
        cities.append(cc2_bah)
        weights.append(probs[preds[i]])


    print medLons,medLats
    if city[0]!=None:
        city = city[0].split('-')[0].title()+', '+city[0].split('-')[-1].upper()
    else:
        city = ''
    print city
    return medLat,medLon,feats,entropyW,KLW,[1],city,cities

'''
def geolocate_multiple(text):
    global vectorizer,clf, classLatMedian, classLonMedian

    classLatMean, classLonMedian, classLatMedian, classLonMean, userLocation, categories, trainUsers, trainClasses, testUsers,testClasses, devUsers, devClasses = pickle.load(open('C:/Users/bahar/Desktop/model100h.pkl','rb'))
    del userLocation, trainUsers, trainClasses, testUsers,testClasses, devUsers, devClasses
    clf = pickle.load(open('C:/Users/bahar/Desktop/clfModel100h.pkl','rb'))
    vectorizer = pickle.load(open('C:/Users/bahar/Desktop/vectorizer100h.pkl','rb'))


#    text = "here is melbourne and sydney"
    X_test = [text]
    X_test = vectorizer.transform(X_test)
    features = vectorizer.get_feature_names()


    pred = clf.predict(X_test)[0]
    prediction = categories[pred]
    print prediction
    probs = clf.predict_proba(X_test)[0]
    print probs.argmax()
    print max(probs)
    #print probs[-10:]
    print probs.argsort()[-10:]
    preds = probs.argsort()[:-10:-1]
    print preds
    
    
    indexes = X_test.nonzero()
    feats = {features[i]:X_test[0,i] for i in indexes[1]}
    feats = sorted(feats.items(), key=lambda x: x[1],reverse = True)[:5]
    print feats

#pred = clf.predict_proba(X_test)
#print pred
#print pred[0][849]
#print dir()
    medLons = []
    medLats = []
    weights = []
    for i in range(0, len(preds)):
        prediction = categories[preds[i]]
        medianlat = classLatMedian[prediction]
        medianlon = classLonMedian[prediction]
        meanlat = classLatMean[prediction]
        meanlon = classLonMean[prediction]
        predictionCoordinate = 'median'

        cc2_bah = lib_grid_search.zoom_search(medianlat,medianlon)
        print cc2_bah
        medLats.append(medianlat)
        medLons.append(medianlon)
        weights.append(probs[preds[i]])
    print weights
    return medLats,medLons,feats,weights
'''

@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="static")


@route('/map')
def show():
    return  template('index', lats=[55.67], longs=[12.56],text='',entropy=[],mentionsLocs=[],KLD=[], accountName='',features=[],weights=[0],city='',filledText='',cities=[])

@post('/map')
def do_show():
    accountName = request.forms.get('name')
    locations = []
    mentions = []
    if accountName!='':
        text,locations,mentions = catch_account(accountName)
        print locations
        print mentions
        mentionsLocs=  mentions_loc(mentions)
        filledText=''
    else:
        filledText = request.forms.get('tweet')
        accountName = ''
        text = filledText
        mentions = []
        mentionsLocs = []
    #text = 'hello to melbourne'
    lats,longs,feats,entropy,KL,weights,city,cities = geolocate(text)


    print city
    
    return  template('index', lats=lats, longs=longs,text=text[:200],mentionsLocs=mentionsLocs,accountName=accountName,entropy=entropy,KLD=KL,features=feats,weights=weights,city=city,filledText=filledText,cities=cities)
    

#classLatMean, classLonMedian, classLatMedian, classLonMean, userLocation, categories, trainUsers, trainClasses, testUsers,testClasses, devUsers, devClasses = pickle.load(open('C:/Users/bahar/Desktop/modelall.cpkl','rb'))
#del userLocation, trainUsers, trainClasses, testUsers,testClasses, devUsers, devClasses
#clf = cPickle.load(open('C:/Users/bahar/Desktop/clfModelall.cpkl','rb'))
#vectorizer = pickle.load(open('C:/Users/bahar/Desktop/vectorizerall.cpkl','rb'))

run(host='localhost', port=8080, debug=True)
