from tornado import gen,web
from tornado import websocket
import json,os,time
import pymongo
from pprint import pprint
from bson.objectid import ObjectId #deal with object pymongo
from bson.code import Code
from bson import ObjectId


templateurl = "../template/"

class BaseHandler(web.RequestHandler):
	def get_current_user(self):
		user_id = self.get_secure_cookie("id")
		if not user_id: return None
		user_name = str(self.get_secure_cookie("name"),'utf-8')
		user_status = str(self.get_secure_cookie("status"),'utf-8')
		user = {
			'user':str(user_id,'utf-8'),
			'name':user_name,
			'status':user_status
		}
		print("in current user")
		print(type(user_id))

		return user

class PrivateChatHandler(BaseHandler):
	@web.authenticated
	def get(self):
		print("pchat")
		pprint(self.current_user)
		count = 0

		f = open("template/test.txt")
		"""
		for msg in f:
			if if msg[0:msg.index("#")] == username
		"""
		for line in f:
			count = count + 1

		f.seek(0);

		self.render(templateurl+"privatechat.html",user_name=self.current_user['name'], status=self.current_user['status'], id_last_index=0, filename=f, username="1", friend_name="2", posts_no=count,user_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

class GroupChatHandler(BaseHandler):
	@web.authenticated
	def get(self):
		f = open("template/test.txt")

		count = 0

		for line in f:
		  count = count + 1

		f.seek(0)

		self.render(templateurl+"groupchat.html", user_name=self.current_user['name'], status=self.current_user['status'], id_last_index=0, group_name="Eqraa", posts_no=count, chat_members=["2","3","4"], filename=f, username="1", group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

class HomeHandler(BaseHandler):
	@web.authenticated
	def get(self):
		print("++++++++++++++++++++++++++++++++")
		print(type(self.current_user['name']))
		print("++++++++++++++++++++++++++++++++")
		print(self.current_user)
		self.render(templateurl+"home.html", user_name=self.current_user['name'], status=self.current_user['status'], group_name="Eqraa", posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

#handling signup in db and cookies (registeration and login)
class SignupHandler(BaseHandler):
	#@web.authenticated
	def post(self):
		#insert user info
		db = self.application.database
		username=self.get_argumeQnt("signupname")
		email=self.get_argument("signupemail")
		pwd=self.get_argument("signuppwd")
		new_user = {"name":username,"password":pwd,"email":email,"status":'on','groups_id':[],'friendId':[]}
		try:
			user_id = db.users.insert(new_user)
			self.set_secure_cookie("id",str(user_id))
			self.set_secure_cookie("name", username)
			self.set_secure_cookie("status", 'on')
			self.render(templateurl+"home.html", user_name=username, status='on', group_name="Eqraa", posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")
		except pymongo.errors.DuplicateKeyError:
			# error in signup if duplicated name
			self.redirect("/?sp=1")


class GroupsHandler(BaseHandler):
	@web.authenticated
	def get(self):
		groupslist_in=[]
		groupslist_notin=[]
		owner=[]
		db = self.application.database
		user_id =ObjectId(self.current_user['user'])

		#pprint(type(user_id))
		groups=db.users.find({'_id':user_id},{'groups_id':1,'_id':0})
		for g in groups:
			for group in g["groups_id"]:
				name=db.groups.find({'_id':group})

				for n in name:
					pprint(n)
					groupslist_in.append({'_id':n['_id'],'name':n['name']})
					if n['owner'] == user_id:
						owner.append(n['_id'])
			notin_name=db.groups.find({'_id':{'$nin':g["groups_id"]}},{'name':1})
			for nin in notin_name:
				groupslist_notin.append(nin)
		pprint(owner)

		# db.users.find({name:userName}).forEach(function(user){ db.groups.find({user:user._id}).forEach(function(group) { print(group.name) }) })

		self.render(templateurl+"groups.html", user_name=self.current_user['name'], status=self.current_user['status'], groups_list=groupslist_in,nin_grouplist=groupslist_notin, owner=owner, posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

class PeopleHandler(BaseHandler):
	@web.authenticated
	def get(self):
		db = self.application.database
		userName =self.current_user['name']
		print(userName)
		friends_list_in=[]
		friends_list_notin=[]
		db = self.application.database
		user_id =self.current_user['name']
		#pprint(type(user_id))
		friends=db.users.find({'name':user_id},{'friendId':1,'_id':0})
		for f in friends:
			for friend in f["friendId"]:
				name=db.users.find({'_id':friend},{'name':1})
				for n in name:
					friends_list_in.append(n)
			notin_name=db.users.find({'_id':{'$nin':f["friendId"]}},{'name':1})
			for nin in notin_name:
				friends_list_notin.append(nin)
		self.render(templateurl+"people.html", user_name=self.current_user['name'], status=self.current_user['status'], friend_nin_list=friends_list_notin,friend_in_list=friends_list_in, posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")
# Handler to Create Group
class CreateGroupHandler(BaseHandler):
	@web.authenticated
	def get(self):
		self.render(templateurl+"creategroup.html")
	@web.authenticated	
	def post(self):
		
		db = self.application.database
		groupname = self.get_argument("groupname")
		owner=ObjectId(self.current_user['user'])
		group_id = db.groups.insert({'name':groupname,'owner':owner})
		db.users.update({"_id":owner},{"$push":{'groups_id':group_id}})
		self.redirect("/groups")


# class ChatBotHandler(BaseHandler):
# 	@web.authenticated
# 	def get(self):
# 		f = open("template/test.txt")

# 		count = 0

# 		for line in f:
# 		  count = count + 1

# 		f.seek(0)

# 		self.render(templateurl+"chatbot.html",user_name=self.current_user['name'], status=self.current_user['status'], id_last_index=0, filename=f, username="1", friend_name="2", posts_no=count,user_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")
		self.render(templateurl+"people.html", user_name=self.current_user['name'], status=self.current_user['status'], group_name="Eqraa", posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")
"""
#class to add friend
class AddFriendHandler(BaseHandler):
	@web.authenticated
	def get(self):
		userId = ObjectId(self.current_user['user'])
		# str(self.get_secure_cookie("id"),'utf-8')
		#print(userId)
		#open connection with database
		db = self.application.database
		# iterate in users to find matched one
		userss=db.users.find({"_id":ObjectId(userId)})
		for users in userss:
			print(users)
		#static adding friend in dbs using id of another one then trying to do it auto
		#adding only id of friends
		reqId= ObjectId("58b5b1845f4a5505a3c40c57")
		# if reqId not in db.users.find({'_id':ObjectId(userId)},{friendId:1,_id:0}).forEach(function(frind){test=db.users.find({_id:{$in:frind.friendId}})}):
		# 	print("duplicates")
		# else:
		db.users.update({"_id":ObjectId(userId)},{"$push":{"friendId":reqId}})

		# x []= Code(db.users.find({'_id':ObjectId(userId)},{"friendId":1,"_id":0}).forEach(function(frind){test=db.users.find({reqId:{'$in':'frind.friendId'}}).forEach(function(u){print(u.name)})}))
		#	print(x)
		# but the above code will allow dublicated
		#we need to verify if it's exist before or not may be try to remove it if it's exist before
"""
class AddingHandler(BaseHandler):
	@web.authenticated
	def post(self):
		uid = ObjectId(self.current_user['user'])
		fgadd=self.get_argument("add")
		addid=ObjectId(self.get_argument("join"))
		#open connection with database
		db = self.application.database
		if fgadd== "friend":
			add = "friendId"
		elif fgadd== "group":
			add = "groups_id"
		#__TODO__Exceptions handling
		print("adding")
		print(fgadd)
		print(addid)
		# 	print("duplicates")
		db.users.update({"_id":uid},{"$push":{add:addid}})
		if fgadd== "friend":
			self.redirect("/people")
		elif fgadd== "group":
			self.redirect("/groups")

class BlockHandler(BaseHandler):
	@web.authenticated
	def post(self):
		#__TODO__ handel fun return
		#fgblock string string refering to block friend or Group
		fgblock=self.get_argument("block")
		removeid=ObjectId(self.get_argument("remove"))
		db = self.application.database
		#__TODO__ get removeid from interface
		#removeid=ObjectId("58b5ca548d46858f7030f216")#user
		#removeid=ObjectId("58b5c9b68d46858f7030f215")#group
		uid=ObjectId(self.current_user['user'])
		print(fgblock)
		print(removeid)
		if fgblock== "friend":
			block = "friendId"
		elif fgblock== "group":
			block = "groups_id"
		#__TODO__Exceptions handling
		update=db.users.update_one({"_id":uid},{"$pull":{block:removeid}})
		if fgblock== "friend":
			self.redirect("/people")
		elif fgblock== "group":
			self.redirect("/groups")

		pprint(update.modified_count)
#########################################################################################3
"""
#creating handler for create group
# don't work
class CreateGroupHandler(BaseHandler):
	@web.authenticated
	def get(self):
		userId = str(self.get_secure_cookie("id"),'utf-8')
		groupNameCreate=self.get_argument("gx")
		print(gx)
		#db = self.application.database
"""

#handling websocket
clients = []
class WSHandler(websocket.WebSocketHandler,BaseHandler):
	pass
"""
	pprint(clients)
	print("ws")
	#@web.authenticated
	def open(self):
		# print(self.current_user)
		if self.current_user:
			print("ws")
			client={'id':self.current_user['user'],'info':self,'name':self.current_user['name']}
			pprint(client)
			clients.append(client)
	def on_message(self,message):
		pprint(clients)
		msg=json.loads(message)
		pprint(msg)
"""
		#db = self.application.databas
##########################################
class LogoutHandler(BaseHandler):
	@web.authenticated
	def get(self):
		self.clear_cookie("id")
		self.redirect("/")
