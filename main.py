from tornado import web,ioloop,httpserver,options
from handlers.handlers import *
from pymongo import MongoClient
from pprint import pprint
from tornado.options import define, options
from bson.code import Code
import os
import uuid
import json
from tornado import websocket

define("port", default=7070, help="run on the given port", type=int)


class Application(web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/signup",SignupHandler),
			(r"/pchat",PrivateChatHandler),
			(r"/ws",WSHandler),
			(r"/gchat",GroupChatHandler),
			(r"/gws",GWSHandler),
			(r"/home",HomeHandler),
			(r"/groups",GroupsHandler),
			(r"/people",PeopleHandler),
			(r"/add",AddingHandler),
			(r"/blockfriend",BlockHandler),
			#create group
			(r"/creategroup",CreateGroupHandler),
			(r"/statuschange",StatusChangeHandler),
			(r"/LogOut",LogoutHandler),
			(r"/removemsgs",RmmsgsHandler)

			]

		settings = dict(
			autoescape=None,
			autoreload=True,
			debug=True,
			static_path="static",
			cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
			login_url="/",
		)
		web.Application.__init__(self, handlers, **settings)
		self.con = MongoClient('localhost', 27017)
		print(self.con)
		self.database = self.con["Chat"]

class MainHandler(BaseHandler):

	cls1 = "active"
	cls2 = ""
	signup_disp = ""
	login_disp = ""
	def get(self):

		print("///")
		if self.get_argument("sp",False):
			self.render("template/index.html",class_tag1=self.cls1,class_tag2=self.cls2, error=False, signup_display=self.signup_disp, login_display=self.login_disp,sp_error=True)
		if not self.current_user:
			self.render("template/index.html",class_tag1=self.cls1,class_tag2=self.cls2, error=False, signup_display=self.signup_disp, login_display=self.login_disp,sp_error=False)
		else:
			self.redirect("/home")
	def post(self):
		db = self.application.database
		username=self.get_argument("username")
		pwd=self.get_argument("pwd")
		find_cond={"$and":[{'name':username},{'password':pwd}]}
		users = db["users"].find(find_cond)
		if users.count() == 0:

			self.cls2 = "active"
			self.cls1 = ""
			self.signup_disp = "display:none;"
			self.login_disp = "display:block;"
			self.render("template/index.html",class_tag1=self.cls1,class_tag2=self.cls2, error=True, signup_display=self.signup_disp, login_display=self.login_disp,sp_error=False)
		else:
			#LOGIN
			#Add username to cookies
			#redirect to home page and start session
			for c in users:
				self.set_secure_cookie("id",str(c['_id']))
				self.set_secure_cookie("name", c['name'])
				self.set_secure_cookie("status", c['status'])
				
			self.redirect("/home")

"""
@ Main Function
"""
def main():
	options.parse_command_line()
	http_server = httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	ioloop.IOLoop.current().start()
	rh = RoomHandler()
if __name__ == "__main__":
	main()
