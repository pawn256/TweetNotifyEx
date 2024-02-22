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
        self.str_main_js_url="https://abs.twimg.com/responsive-web/client-web/main.5d39ee1a.js" # There is Bearer Token in this js file.

        self.str_bearer_token=''
        self.get_str_bearer_token()

        self.headers={}
        self.headers['authorization']='Bearer %s'%(self.str_bearer_token)

        print self.headers

        self.str_x_guest_token=''
        self.get_str_x_guest_token()

        self.headers['x-guest-token']=self.str_x_guest_token
        print self.headers

        obj_j={}
        obj_j["variables"]={
            "screen_name": self.str_user_name,
            "withSafetyModeUserFields": True
        }
        obj_j["features"]={
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "subscriptions_verification_info_is_identity_verified_enabled": True,
            "subscriptions_verification_info_verified_since_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True
        }
        obj_j["fieldToggles"]={
            "withAuxiliaryUserLabels": False
        }
        self.str_user_by_screen_name_url="https://twitter.com/i/api/graphql/k5XapwcSikNsEsILW5FvgA/UserByScreenName?variables=%s&features=%s&fieldToggles=%s"%(urllib.quote(json.dumps(obj_j["variables"])),urllib.quote(json.dumps(obj_j["features"])),urllib.quote(json.dumps(obj_j["fieldToggles"]))) # This is needed for getting id or rest_id by username.
        print "str_user_by_screen_name_url:",self.str_user_by_screen_name_url

        self.str_user_id=''
        self.get_str_user_id()
        print "str_user_id:",self.str_user_id

        # This userId is rest_id from UserBySceenName.
        obj_j={}
        obj_j["variables"]={
            "userId": self.str_user_id,
            "count": 20,
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True
        }
        obj_j["features"]={
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        }
        self.str_user_tweets_url="https://twitter.com/i/api/graphql/LJwZwXzqk7wHyXPa3SQt4Q/UserTweets?variables=%s&features=%s"%(urllib.quote(json.dumps(obj_j['variables'])),urllib.quote(json.dumps(obj_j['features'])))
        print "str_user_tweets_url:",self.str_user_tweets_url
        self.str_top_tweet=''
        self.str_pinned_tweet=''

    def print_debug(self):
        print "self.str_bearer_token:",self.str_bearer_token
        print "self.headers:",self.headers
        print "self.str_x_guest_token:",self.str_x_guest_token
        print "self.headers:",self.headers
        print "self.str_user_by_screen_name_url:",self.str_user_by_screen_name_url
        print "self.str_user_id:",self.str_user_id
        print "self.str_user_tweets_url:",self.str_user_tweets_url

    def get_str_bearer_token(self):
        obj_r=requests.get(self.str_main_js_url)
        self.str_bearer_token=re.findall(r'"Bearer (.*?)"',obj_r.text)[0] # Maybe there is more good method. This get bearer token by grep.

    def get_str_x_guest_token(self):
        self.url="https://twitter.com/"+self.str_user_name
        obj_r = requests.get(self.url,headers={"user-agent":"curl/7.88.1"}) # If there isn't user agent, return 400 bad request. so specified.
        try:
            self.str_x_guest_token=re.findall(r'"gt=(.*?);',obj_r.text)[0] # i hate this code, it might change logic.
        except Exception as e:
            print "get_str_x_guest_token failed."

    def get_str_user_id(self):
        obj_r=requests.get(self.str_user_by_screen_name_url,headers=self.headers)
        #print obj_r.text
        obj_j=json.loads(obj_r.text)
        self.str_user_id=obj_j['data']['user']['result']['rest_id']

    def get_tweets(self): # User id is rest_id.
        self.init()
        obj_r=requests.get(self.str_user_tweets_url,headers=self.headers)
        obj_j=json.loads(obj_r.text)
        try:
            for tweet in obj_j['data']['user']['result']['timeline_v2']['timeline']['instructions']:
                if 'entries' in tweet:
                    self.str_top_tweet = tweet['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy']['full_text'] # top tweet
                    break
            print self.str_top_tweet
            self.strip_top_tweet_text_for_tcl()
        except Exception as e:
            print "get_tweets Error str_top_tweet:",e
            #self.print_debug()

        try:
            for tweet in obj_j['data']['user']['result']['timeline_v2']['timeline']['instructions']:
                if 'entry' in tweet:
                    self.str_pinned_tweet = tweet['entries'][0]['content']['itemContent']['tweet_results']['result']['legacy']['full_text'] # pinned tweet
                    break
            print self.str_pinned_tweet
            self.strip_pinned_tweet_text_for_tcl()
        except Exception as e:
            print "get_tweets Error str_pinned_tweet:",e
            #self.print_debug()

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
        return self.str_top_tweet.encode('utf-8')

    def get_str_pinned_tweet(self):
        return self.str_pinned_tweet.encode('utf-8')


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
    print "str_tmp_pinned_tweet:",str_tmp_pinned_tweet
    print "str_tmp_top_tweet:",str_tmp_top_tweet
    notify(str_user_name,str_tmp_pinned_tweet)
    notify(str_user_name,str_tmp_top_tweet)
      
    while True:
        try:
            obj_get_tweet.get_tweets()
            if str_tmp_pinned_tweet != obj_get_tweet.get_str_pinned_tweet() and len(obj_get_tweet.get_str_pinned_tweet()) != 0:
                str_tmp_pinned_tweet=obj_get_tweet.get_str_pinned_tweet()
                print "str_tmp_pinned_tweet:",str_tmp_pinned_tweet
                notify(str_user_name,str_tmp_pinned_tweet)

            if str_tmp_top_tweet != obj_get_tweet.get_str_top_tweet() and len(obj_get_tweet.get_str_top_tweet()) != 0:
                str_tmp_top_tweet=obj_get_tweet.get_str_top_tweet()
                print "str_tmp_top_tweet:",str_tmp_top_tweet
                notify(str_user_name,str_tmp_top_tweet)

            time.sleep(10)
        except Exception as e:
            print "TweetNotify Error!!: %s"%(e)
            #obj_get_tweet.print_debug()
            time.sleep(3)

if __name__ == '__main__':
    main()
