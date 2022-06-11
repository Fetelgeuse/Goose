import aminoed 
import random 
import sqlite3 
import time 

from aminoed import Event 
from threading import RLock 
from colored import fg


client = aminoed.Client()
lock = RLock()
db_game = sqlite3.connect("game.db", check_same_thread=False)
game_cursor = db_game.cursor()

game_cursor.execute("""CREATE TABLE IF NOT EXISTS users (
	nickname TEXT, 
	id TEXT, 
	iq INTEGER NOT NULL DEFAULT 1,
	iq_time Integer
	)""")
db_game.commit()


async def sql_game(query):
    def callback():
        try:
        	lock.acquire(True)
        	result = game_cursor.execute(query).fetchone()
        	db_game.commit()
        	return result
        finally: lock.release()
    return await client._loop.run_in_executor(None, callback)
    
    
@client.command("upiq", "/")
async def upiq(event: Event):
    
    new_iq = random.randint(1,3)
    current_time = round(time.time())
    luck = random.randint(0, 100)
    	    	
    try:
    	game = await sql_game(f"SELECT * FROM users where id = '{event.uid}'")
    	nickname, id, iq, iq_time = game or list(range(4))    	
    	if not game:
    		await sql_game(f"INSERT INTO users VALUES {(event.author.nickname, event.uid, new_iq, current_time)}")
    		await event.reply(f"🌼: Your goose has become smarter! :3 \n\n🧠: + {new_iq} iq \nTotal: {iq+new_iq} iq")
    		return    		
    		
    	if current_time - 120 < iq_time:
    		total = int(current_time - 120)
    		await event.reply(f"🌼: Wait a bit, your goose is resting! \n\n⏳:  {(iq_time - total)//60}m {(iq_time - total) - ((iq_time - total)//60 * 60)}s left :3")
    		return
    	
    	if luck >= 10:
    		await sql_game(f"UPDATE users SET iq = {iq+new_iq}, iq_time = {current_time} WHERE id = '{event.uid}'")
    		await event.reply(f"🌼: Your goose has become smarter!  :3 \n\n🧠: + {new_iq} iq \nTotal: {iq+new_iq} iq")
    	else:
    		 await sql_game(f"UPDATE users SET iq = {iq-new_iq}, iq_time = {current_time} WHERE id = '{event.uid}'")
    		 await event.reply(f"🌼: Your goose got dumber! :< \n\n🧠: - {new_iq} iq \nTotal: {iq-new_iq} iq")
    		    	
    except Exception as goose: print(goose)
    
    
@client.command("top", "/")
async def xp(event: Event):
	try:
		await sql_game(f"UPDATE users SET nickname = '{event.author.nickname}' WHERE id = '{event.uid}'")
		index = 0
		top = ''
		try:
			lock.acquire(True)
			for i in zip(game_cursor.execute(f"SELECT nickname, iq FROM users ORDER BY iq DESC")):
				index += 1
				top += f'{index}. {i[0][0]} — {i[0][1]} iq\n'
				if index == 10:
					break
		finally: lock.release()
		await event.reply(f"[cb]The smartest geese :3  :3 \n\n{top}")
	except Exception as goose: print(goose)
	
	
@client.command("everyone", "_")
async def everyone(event: Event):
	users = list()
	community = await client.set_community(event.ndcId)
	
	try:
		user_ids = await community.get_chat_users(event.threadId)
		for user in user_ids:
			users.append(user.uid)
		await event.reply("🦆", mentions=users)
	except Exception as goose: print(goose)
    
    
@client.on("message")
async def on_message(event: Event):
	
	print(
		fg(121), str(event.createdTime)[11:19], 
		fg(166), "||", 
		fg(80), (await client.get_community_info(event.ndcId)).name, 
		fg(166), "||", 
		fg(195), event.author.nickname,
		fg(166), "||", 
		fg(203), event.content, 
		fg(166), "||", 
		fg(209), event.type
	)
	
	
if __name__ == "__main__":
	
	print("Connected!")
	client.start(email="", password="", sid=None)
