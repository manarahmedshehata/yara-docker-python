from tornado import gen,web
from tornado import websocket
import json,os,time
import pymongo
from pprint import pprint
from bson.objectid import ObjectId #deal with object pymongo
from bson.code import Code
from bson import ObjectId
import uuid
import tornado.ioloop
import tornado.web

templateurl = "../template/"


class RoomHandler(object):
    """Store data about connections, rooms, which users are in which rooms, etc."""
    def __init__(self):
        self.client_info = {}  # for each client id we'll store  {'wsconn': wsconn, 'room':room, 'nick':nick}
        self.room_info = {}  # dict  to store a list of  {'cid':cid, 'nick':nick , 'wsconn': wsconn} for each room
        self.roomates = {}  # store a set for each room, each contains the connections of the clients in the room.

    def add_roomnick(self, room, nick):
        """Add nick to room. Return generated clientID"""
        # meant to be called from the main handler (page where somebody indicates a nickname and a room to join)
        cid = uuid.uuid4().hex  # generate a client id.
        if not room in self.room_info:  # it's a new room
            self.room_info[room] = []
        c = 1
        nn = nick
        nir = self.nicks_in_room(room)
        while True:
            if nn in nir:
                nn = nick + str(c)
            else:
                break
            c += 1

        self.client_info[cid] = {'room': room, 'nick': nn}  # we still don't know the WS connection for this client
        self.room_info[room].append({'cid': cid, 'nick': nn})
        return cid

    def add_client_wsconn(self, client_id, conn):
        """Store the websocket connection corresponding to an existing client."""
        self.client_info[client_id]['wsconn'] = conn
        cid_room = self.client_info[client_id]['room']

        if cid_room in self.roomates:
            self.roomates[cid_room].add(conn)
        else:
            self.roomates[cid_room] = {conn}

        for user in self.room_info[cid_room]:
            if user['cid'] == client_id:
                user['wsconn'] = conn
                break
        # send "join" and and "nick_list" messages
        self.send_join_msg(client_id)
        nick_list = self.nicks_in_room(cid_room)
        cwsconns = self.roomate_cwsconns(client_id)
        self.send_nicks_msg(cwsconns, nick_list)

    def remove_client(self, client_id):
        """Remove all client information from the room handler."""
        cid_room = self.client_info[client_id]['room']
        nick = self.client_info[client_id]['nick']
         # first, remove the client connection from the corresponding room in self.roomates
        client_conn = self.client_info[client_id]['wsconn']
        if client_conn in self.roomates[cid_room]:
            self.roomates[cid_room].remove(client_conn)
            if len(self.roomates[cid_room]) == 0:
                del(self.roomates[cid_room])
        r_cwsconns = self.roomate_cwsconns(client_id)
        # filter out the list of connections r_cwsconns to remove clientID
        r_cwsconns = [conn for conn in r_cwsconns if conn != self.client_info[client_id]['wsconn']]
        self.client_info[client_id] = None
        for user in self.room_info[cid_room]:
            if user['cid'] == client_id:
                self.room_info[cid_room].remove(user)
                break
        self.send_leave_msg(nick, r_cwsconns)
        nick_list = self.nicks_in_room(cid_room)
        self.send_nicks_msg(r_cwsconns, nick_list)
        if len(self.room_info[cid_room]) == 0:  # if room is empty, remove.
            del(self.room_info[cid_room])
            print("Removed empty room %s" % cid_room)

    def nicks_in_room(self, rn):
        """Return a list with the nicknames of the users currently connected to the specified room."""
        nir = []  # nicks in room
        for user in self.room_info[rn]:
            nir.append(user['nick'])
        return nir

    def roomate_cwsconns(self, cid):
        """Return a list with the connections of the users currently connected to the room where
        the specified client (cid) is connected."""
        cid_room = self.client_info[cid]['room']
        r = []
        if cid_room in self.roomates:
            r = self.roomates[cid_room]
        return r


    def send_join_msg(self, client_id):
        """Send a message of type 'join' to all users connected to the room where client_id is connected."""
        nick = self.client_info[client_id]['nick']
        r_cwsconns = self.roomate_cwsconns(client_id)
        msg = {"msgtype": "join", "username": nick, "payload": " joined the chat room."}
        pmessage = json.dumps(msg)
        for conn in r_cwsconns:
            conn.write_message(pmessage)

    @staticmethod
    def send_nicks_msg(conns, nick_list):
        """Send a message of type 'nick_list' (contains a list of nicknames) to all the specified connections."""
        msg = {"msgtype": "nick_list", "payload": nick_list}
        pmessage = json.dumps(msg)
        for c in conns:
            c.write_message(pmessage)

    @staticmethod
    def send_leave_msg(nick, rconns):
        """Send a message of type 'leave', specifying the nickname that is leaving, to all the specified connections."""
        msg = {"msgtype": "leave", "username": nick, "payload": " left the chat room."}
        pmessage = json.dumps(msg)
        for conn in rconns:
            conn.write_message(pmessage)


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, room_handler):
        """Store a reference to the "external" RoomHandler instance"""
        self.__rh = room_handler

    def get(self):
        """Render chat.html if required arguments are present, render main.html otherwise."""
        try:
            room = self.get_argument("room")
            nick = self.get_argument("nick")
            cid = self.__rh.add_roomnick(room, nick)
            self.render("templates/chat.html", clientid=cid)
        except tornado.web.MissingArgumentError:
            self.render("templates/main.html")

class ClientWSConnection(websocket.WebSocketHandler):

    def initialize(self, room_handler):
        """Store a reference to the "external" RoomHandler instance"""
        self.__rh = room_handler

    def open(self, client_id):
        self.__clientID = client_id
        self.__rh.add_client_wsconn(client_id, self)
        print("WebSocket opened. ClientID = %s" % self.__clientID)

    def on_message(self, message):
        msg = json.loads(message)
        msg['username'] = self.__rh.client_info[self.__clientID]['nick']
        pmessage = json.dumps(msg)
        rconns = self.__rh.roomate_cwsconns(self.__clientID)
        for conn in rconns:
            conn.write_message(pmessage)

    def on_close(self):
        print("WebSocket closed")
        self.__rh.remove_client(self.__clientID)

if __name__ == "__main__":
    rh = RoomHandler()
    app = tornado.web.Application([
        (r"/", MainHandler, {'room_handler': rh}),
        (r"/ws/(.*)", ClientWSConnection, {'room_handler': rh})],
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(8888)
    print('Simple Chat Server started.')
    print('listening on 8888 ...')
    tornado.ioloop.IOLoop.instance().start()



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

class PrivateChatHandler(websocket.WebSocketHandler,BaseHandler):
	@web.authenticated

	def open(self):
		print("WebSocket opened")

	def on_message(self, message):
		self.write_message(u"You said: " + message['naame'])

	def on_close(self):
		print("WebSocket closed")

	def get(self):
		print("pchat")
		pprint(self.current_user)
		count = 0
		friend_Id = "sara"
		filePath = "chatHistory/" + self.current_user['name'] + "/" + friend_Id
		print(filePath)
		f = open("template/test.txt")

		# for msg in f:
		# 	if msg[0:msg.index("#")] != username:
		# 		pass
		
		for line in f:
			count = count + 1

		f.seek(0);

		self.render(templateurl+"privatechat.html",user_name=self.current_user['name'], status=self.current_user['status'], id_last_index=0, filename=f, username="1", friend_name="2", posts_no=count,user_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

class GroupChatHandler(websocket.WebSocketHandler,BaseHandler):
	@web.authenticated

	# def open(self):
	# 	print("WebSocket opened")

	# def on_message(self, message):
	# 	self.write_message(u"You said: " + message['msg'])

	# def on_close(self):
	# 	print("WebSocket closed")

	def get(self):
		print("pchat")
		pprint(self.current_user)
		count = 0
		friend_Id = "sara"
		filePath = "chatHistory/" + self.current_user['name'] + "/" + friend_Id
		print(filePath)

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
		username=self.get_argument("signupname")
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
		userName = self.get_secure_cookie("name")
		print(userName)
		frnds_list = db.users.find({"name":userName},{"friendId":1})
		# find friends
		# frnds_list = db.users.find({name:userName},{friendId:1}).forEach(function(frind){=db.users.find({_id:{$in:frind.friendId}}).forEach(function(u){print(u.name)})})

		# db = self.application.database
		# userName = self.current_user
		
		# frnds_list = db.users.find({name:userName},{friendId:1})
		# print(userName)
		#find friends
		# #frnds_list = db.users.find({name:userName},{friendId:1}).forEach(function(frind){=db.users.find({_id:{$in:frind.friendId}}).forEach(function(u){print(u.name)})})
		# print(db.users.find({"name":userName},{"name":1}))
		# print(frnds_list)
		# for i in frnds_list.length:
		# 	print(frnds_list[i])

		# others_list = db.users.find({name:{$ne:userName}},{friendId:1}).forEach(function(frnd){db.users.find({$and[{_id:frnd},{name:{$ne:userName}}]},{"name":1})})

		# self.render(templateurl+"people.html", user_name=self.current_user['name'], friends_list=frnds_list, status=self.current_user['status'], group_name="Eqraa", posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

		self.render(templateurl+"people.html", user_name=self.current_user['name'], status=self.current_user['status'], group_name="Eqraa", posts_no="2000",group_avatar="http://cs625730.vk.me/v625730358/1126a/qEjM1AnybRA.jpg")

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
		userID = str(self.get_secure_cookie("id"),'utf-8')
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
