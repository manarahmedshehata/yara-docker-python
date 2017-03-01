from tornado import web,ioloop,httpserver,options
from handlers.ajax import BaseHandler, SignupHandler, PrivateChatHandler, GroupChatHandler, HomeHandler, GroupsHandler, PeopleHandler, CreateGroupHandler
from handlers.ajax import BaseHandler, SignupHandler, PrivateChatHandler,GroupChatHandler, HomeHandler, GroupsHandler, PeopleHandler,AddFriendHandler
#from handlers.ajax import BaseHandler, SignupHandler, PrivateChatHandler, GroupChatHandler, HomeHandler, GroupsHandler, PeopleHan,ler, BlockHandler
from handlers.ajax import *
from pymongo import MongoClient
from pprint import pprint
from tornado.options import define, options
from bson.code import Code

define("port", default=7070, help="run on the given port", type=int)


class Application(web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/signup",SignupHandler),
			(r"/pchat",PrivateChatHandler),
			(r"/gchat",GroupChatHandler),
			(r"/home",HomeHandler),
			(r"/groups",GroupsHandler),
			(r"/people",PeopleHandler),
			(r"/addgroup",CreateGroupHandler),
			# (r"/chatbot",ChatBotHandler)
			#editing people friend requist
			(r"/addfriend",AddFriendHandler),
			(r"/blockfriend",BlockHandler),
			#create group
			(r"/createGroup",CreateGroupHandler)
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
			#rereender to error page or ajax call "Wrong username or pwd"
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
				#self.set_secure_cookie("status", c['status'])
				self.set_secure_cookie("status", 'on')
			self.redirect("/home")
			#self.render("template/home.html")
			#self.render("template/index.html",class_tag1=cls1,class_tag2=cls2, label_message=label_msg, signup_display=signup_disp, login_display=login_disp)
"""
@ Main Function
"""
def main():
	options.parse_command_line()
	http_server = httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()

#db.users.find({'_id':ObjectId("58b169725d467e34b3718613")},{frinds:1,_id:0}).forEach(function(frind){db.users.find({$and:[{_id:{$nin:frind.frinds}},{_id:{$ne:ObjectId("58b169725d467e34b3718613")}}]}).forEach(function(u){print(u.name)})})
#db.users.find({'_id':ObjectId("58b097a427e114d654b36ceb")},{frinds:1,_id:0}).forEach(function(frind){test=db.users.find({_id:{$in:frind.frinds}}).forEach(function(u){print(u.name)})})
