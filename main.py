#!/usr/bin/python

import re
import os
import json
import urllib
import sys
import time
import requests
sys.path.append(os.environ['TOOLS_DIR'])

import Notify

reload(sys)
sys.setdefaultencoding('utf-8')

class getTweet():
    def __init__(self,str_user_name):
        self.str_user_name=str_user_name
        self.init()

    def init(self):
        self.str_main_js_url="https://abs.twimg.com/responsive-web/client-web/main.99efbbf6.js" # There is Bearer Token in this js file.
        self.str_activate_json_url="https://api.twitter.com/1.1/guest/activate.json" # There is x-guest-token in this file. But this file need Bearer Token.

        self.str_bearer_token=''
        self.get_str_bearer_token()

        self.headers={}
        self.headers['authorization']='Bearer %s'%(self.str_bearer_token)

        print self.headers

        self.str_x_guest_token=''
        self.get_str_x_guest_token()

        self.headers['x-guest-token']=self.str_x_guest_token
        print self.headers

        obj_j=json.loads('{"screen_name":"%s","withSafetyModeUserFields":true,"withSuperFollowsUserFields":true}'%(self.str_user_name))
        self.str_user_by_screen_name_url="https://twitter.com/i/api/graphql/Bhlf1dYJ3bYCKmLfeEQ31A/UserByScreenName?variables="+urllib.quote(json.dumps(obj_j)) # This is needed for getting id or rest_id by username.
        print "str_user_by_screen_name_url:",self.str_user_by_screen_name_url

        self.str_user_id=''
        self.get_str_user_id()
        print "str_user_id:",self.str_user_id

        obj_j=json.loads('{"userId":"%s","count":40,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true,"__fs_responsive_web_like_by_author_enabled":false,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false,"__fs_responsive_web_edit_tweet_api_enabled":false}'%(self.str_user_id)) # This userId is rest_id from UserBySceenName.
        self.str_user_tweets_url="https://twitter.com/i/api/graphql/07VfD4dpV9RcW5dsbCjYuQ/UserTweets?variables="+urllib.quote(json.dumps(obj_j))
        print "str_user_tweets_url:",self.str_user_tweets_url
        self.str_top_tweet=''
        self.str_pinned_tweet=''

    def get_str_bearer_token(self):
        obj_r=requests.get(self.str_main_js_url)
        self.str_bearer_token=re.findall(r'"Web-12"\,s="(.*?)"',obj_r.text)[0] # Maybe there is more good method. This get bearer token by grep.

    def get_str_x_guest_token(self):
        obj_r=requests.post(self.str_activate_json_url,headers=self.headers) # It need to send post request without request deta for getting x-guest-token.
        print obj_r.text
        obj_j=json.loads(obj_r.text)
        self.str_x_guest_token=obj_j['guest_token']

    def get_str_user_id(self):
        obj_r=requests.get(self.str_user_by_screen_name_url,headers=self.headers)
        obj_j=json.loads(obj_r.text)
        self.str_user_id=obj_j['data']['user']['result']['rest_id']

    def get_tweets(self): # User id is rest_id.
        obj_r=requests.get(self.str_user_tweets_url,headers=self.headers)
        obj_j=json.loads(obj_r.text)
        try:
            self.str_top_tweet=obj_j['data']['user']['result']['timeline_v2']['timeline']['instructions'][1]['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy']['full_text'] # top tweet
            self.str_top_tweet
            self.strip_top_tweet_text_for_tcl()
        except Exception as e:
            print e

        try:
            self.str_pinned_tweet=obj_j['data']['user']['result']['timeline_v2']['timeline']['instructions'][2]['entry']['content']['itemContent']['tweet_results']['result']['legacy']['full_text'] # pinned tweet
            self.str_pinned_tweet
            self.strip_pinned_tweet_text_for_tcl()
        except Exception as e:
            print e

    def strip_text_for_tcl(self,str_text): 
        char_list = [str_text[i] for i in range(len(str_text)) if ord(str_text[i]) in range(65536)]
        str_text=''
        for i in char_list:
            str_text=str_text+i
        return str_text

    def strip_top_tweet_text_for_tcl(self): # Unicode range that Tcl allow is from U+0000 to U+FFFF. In other words, It can't use Emoji. So, It remove that characters.
        self.str_top_tweet=self.strip_text_for_tcl(self.str_top_tweet)

    def strip_pinned_tweet_text_for_tcl(self): # Unicode range that Tcl allow is from U+0000 to U+FFFF. In other words, It can't use Emoji. So, It remove that characters.
        self.str_pinned_tweet=self.strip_text_for_tcl(self.str_pinned_tweet)

    def get_str_top_tweet(self):
        return self.str_top_tweet

    def get_str_pinned_tweet(self):
        return self.str_pinned_tweet


def notify(title,text):
    obj_notify=Notify.Notify(title)
    obj_notify.notify()
    obj_notify.setText(text)
    obj_notify.setButton()
    obj_notify.wavplay()
    obj_notify.start()

def main():
    str_user_name=sys.argv[1]
    obj_get_tweet=getTweet(str_user_name)
    obj_get_tweet.get_tweets()
    str_tmp_pinned_tweet=obj_get_tweet.get_str_pinned_tweet()
    str_tmp_top_tweet=obj_get_tweet.get_str_top_tweet()
    notify(str_user_name,str_tmp_pinned_tweet)
    notify(str_user_name,str_tmp_top_tweet)
      
    while True:
        try:
            obj_get_tweet.get_tweets()
            if str_tmp_pinned_tweet != obj_get_tweet.get_str_pinned_tweet():
                str_tmp_pinned_tweet=obj_get_tweet.get_str_pinned_tweet()
                notify(str_user_name,str_tmp_pinned_tweet)

            if str_tmp_top_tweet != obj_get_tweet.get_str_top_tweet():
                str_tmp_top_tweet=obj_get_tweet.get_str_top_tweet()
                notify(str_user_name,str_tmp_top_tweet)

            time.sleep(10)
        except Exception as e:
            print "TweetNotify Error!!: %s"%(e)
            time.sleep(3)

if __name__ == '__main__':
    main()
