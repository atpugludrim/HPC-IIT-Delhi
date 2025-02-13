import sys
import getpass
import signal
from datetime import datetime
import urllib
import urllib.request
import threading
import ssl

class Proxy:
    proxy_set={'phd':61}
    google = 'http://www.google.com'
    STATUS = 0
    VERBOSE = False
    def __init__(self, username, password, proxy_cat='phd'):
        self.username = username
        self.password = password
        self.proxy_cat = proxy_cat
        self.auto_proxy = "http://www.cc.iitd.ernet.in/cgi-bin/proxy."+proxy_cat
        self.urlopener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl._create_unverified_context()), urllib.request.ProxyHandler({'auto_proxy':self.auto_proxy}))
        self.proxy_page_address = 'https://proxy'+str(Proxy.proxy_set[proxy_cat])+'.iitd.ernet.in/cgi-bin/proxy.cgi'
        self.new_session_id()
        self.details()
        

    def is_connected(self):
        proxies = {'http': 'http://proxy'+str(Proxy.proxy_set[self.proxy_cat])+'.iitd.ernet.in:3128'}
        try:
            response = urllib.urlopen(Proxy.google, proxies=proxies).read()
        except Exception as e:
            print(e)
            return "Not Connected"
        if "<title>IIT Delhi Proxy Login</title>" in response:
            return "Login Page"
        elif "<title>Google</title>" in response:
            return "Google"
        else:
            return "Not Connected"

    def get_session_id(self):
        try:
            response = self.open_page(self.proxy_page_address)
        except Exception as e:
            print(e)
            return None
        check_token='sessionid" type="hidden" value="'
        token_index=response.index(check_token) + len(check_token)
        sessionid=""
        for i in range(16):
            sessionid+=str(response[token_index+i])
        return sessionid

    def new_session_id(self):
        self.sessionid = self.get_session_id()
        self.loginform={'sessionid':self.sessionid, 'action':'Validate', 'userid':self.username, 'pass':self.password}
        self.logout_form={'sessionid':self.sessionid, 'action':'logout', 'logout':'Log out'}
        self.loggedin_form={'sessionid':self.sessionid, 'action':'Refresh'}

    def login(self):
        self.new_session_id()
        response = self.submitform(self.loginform)
        if "Either your userid and/or password does'not match." in response:
            return "Incorrect", response
        elif "You are logged in successfully as "+self.username in response:
            def ref():
                if not self.loggedout:
                    res = self.refresh()
                    print ("Refresh",datetime.now())
                    if res=='Session Expired':
                        print ("Session Expired Run Script again")
                    else:
                        self.timer = threading.Timer(60.0,ref)
                        self.timer.daemon = True
                        self.timer.start()
            self.timer = threading.Timer(60.0,ref)
            self.timer.daemon = True
            self.timer.start()
            self.loggedout = False
            return "Success", response
        elif "already logged in" in response:
            return "Already", response
        elif "Session Expired" in response:
            return "Expired", response
        else:
            return "Not Connected", response

    def logout(self):
        self.loggedout = True
        response = self.submitform(self.logout_form)
        if "you have logged out from the IIT Delhi Proxy Service" in response:
            return "Success", response
        elif "Session Expired" in response:
            return "Expired", response
        else:
            return "Failed", response
        
    def refresh(self):
        response = self.submitform(self.loggedin_form)
        if "You are logged in successfully" in response:
            if "You are logged in successfully as "+self.username in response:
                return "Success", response
            else:
                return "Not Logged In"
        elif "Session Expired" in response:
            return "Expired", response
        else:
            return "Not Connected", response

    def details(self):
        for property, value in vars(self).items():
            if Proxy.VERBOSE:
                print (property, ": ", value)

    def submitform(self, form):
        return self.urlopener.open(urllib.request.Request(self.proxy_page_address,urllib.parse.urlencode(form).encode('ascii'))).read().decode('ascii')

    def open_page(self, address):
        return self.urlopener.open(address).read().decode('ascii')


def main():
    def signal_handler(signal, frame):
            print ('\nLogout',user.logout()[Proxy.STATUS])
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    uname = 'aiz21xxxx' # Change this
    passwd = getpass.getpass()
    user = Proxy(username=uname, password=passwd)
    login_status = user.login()[Proxy.STATUS]
    print ('\nLogin',login_status)
    if login_status=="Success":
        signal.pause()
if __name__=="__main__":
    main()
