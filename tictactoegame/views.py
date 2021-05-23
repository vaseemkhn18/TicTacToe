from django.shortcuts import render, redirect
#from django.http import HttpResponse
#from django.http import HttpRequest
from .models import session, connection, status
import random as r
#import json
from django.http import JsonResponse
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils import timezone
#import threading
#import time

# Create your views here.


def isGameover(gid,plr):
	sess = session.objects.filter(sess_id = str(gid))
	stat = status.objects.filter(sess_id = sess[0])
	c1 = str(stat[0].cell_1)
	c2 = str(stat[0].cell_2)
	c3 = str(stat[0].cell_3)
	c4 = str(stat[0].cell_4)
	c5 = str(stat[0].cell_5)
	c6 = str(stat[0].cell_6)
	c7 = str(stat[0].cell_7)
	c8 = str(stat[0].cell_8)
	c9 = str(stat[0].cell_9)
	
	win = [[c1,c4,c7],[c2,c5,c8],[c3,c6,c9],[c1,c2,c3],[c4,c5,c6],[c7,c8,c9],[c1,c5,c9],[c7,c5,c3]]
	if ['X', 'X', 'X'] in win or ['O', 'O', 'O'] in win:
		if plr == "Player 1":
			status.objects.filter(sess_id = sess[0]).update(game_state = "p1")
			status.objects.filter(sess_id = sess[0]).update(game = False)
		else:
			status.objects.filter(sess_id = sess[0]).update(game_state = "p2")
			status.objects.filter(sess_id = sess[0]).update(game = False)
		return "Win"
	
	if c1 and c2 and c3 and c4 and c5 and c6 and c7 and c8 and c9:
		status.objects.filter(sess_id = sess[0]).update(game_state = "ov")
		status.objects.filter(sess_id = sess[0]).update(game = False)
		return "Game_Over"
	else:
		return "Go_On"
	
def entry(request):
    
	action = {
		'entry' : False,
		'new_game' : False,
		'join_game' : False,
		'sid' : 0,
	}
	if(request.POST.get('new')):
		if not request.POST.get('fname'):
			# will send some parameter to show enter name msg
			action['new_game'] = True
			action['sid'] = 123
			return render(request, "entry.html", action)
		else:	
			sid= str(r.randrange(100,999,4))
			while session.objects.filter(sess_id = sid).exists():
				sid= str(r.randrange(100,999,4))
					
			sess = session(sess_id = sid)
			request.session['sess_id'] = sid
			sess.save()
			con = connection()
			ip = getIPaddr(request,sid,'p1')
			con.p1 = str(ip)
			con.sess_id = sess
			con.connected = False
			con.save()
			stat = status()
			stat.sess_id = sess
			stat.save()
			# will send some parameter to show waiting for someone to join msg
			action['new_game'] = True
			action['sid'] = sid
			return redirect('/game/')
		
		
	elif(request.POST.get('join')):
		if not request.POST.get('fname'):
			# will send some parameter to show enter name msg
			action['join_game'] = True
			action['sid'] = 123
			return render(request, "entry.html", action)
		else:
			if not connection.objects.filter(connected = False).exists():
				# will send some parameter to show no game exists to join msg
				action['join_game'] = True
				action['sid'] = 123
				return render(request, "entry.html", action)
			else:
				action['join_game'] = True
				action['sid'] = 123
				return render(request, "entry.html", action)

				
	elif(request.POST.get('con_game')):
		if not request.POST.get('jsid'):
			# will send some parameter to show enter sesson id msg
			action['join_game'] = True
			action['sid'] = 123
			return render(request, "entry.html", action)
		else:
			sess = session.objects.filter(sess_id = str(request.POST.get('jsid')))
			if not session.objects.filter(sess_id = str(request.POST.get('jsid'))).exists():
				# will send some parameter to show invalid sesson id msg
				action['join_game'] = True
				action['sid'] = 123
				return render(request, "entry.html", action)
			elif connection.objects.filter(sess_id = sess[0])[0].connected:
				action['join_game'] = True
				action['sid'] = 123
				return render(request, "entry.html", action)
			else:
				connection.objects.filter(sess_id = sess[0]).update(connected = True)
				ip = getIPaddr(request,request.POST.get('jsid'),'p2')
				connection.objects.filter(sess_id = sess[0]).update(p2 = str(ip))
				status.objects.filter(sess_id = sess[0]).update(game = True)
				request.session['sess_id'] = str(request.POST.get('jsid'))
				# Redirected to game everything was perfect
				return redirect('/game/')
	else:
		action['entry'] = True
		action['sid'] = 123
		# will send some parameter to show something went wrong msg
		return render(request, "entry.html", action)

def game(request):
	action = {
		'stat' : 'Not Connected',
		'player' : '',
		'sid' : 0,
		'cell_1' : '',
		'cell_2' : '',
		'cell_3' : '',
		'cell_4' : '',
		'cell_5' : '',
		'cell_6' : '',
		'cell_7' : '',
		'cell_8' : '',
		'cell_9' : '',
		'gstatus' : '',
		'turn' : '',
	}
	try:
		sid = request.session['sess_id']
		action['sid'] = sid
		sess = session.objects.filter(sess_id = str(sid))
		con = connection.objects.filter(sess_id = sess[0])
		stat = status.objects.filter(sess_id = sess[0])
		player = ''
		connection.objects.filter(sess_id = sess[0]).update(timestamp = timezone.now())
		con_p1 = con[0].p1
		con_p2 = con[0].p2
		req_key = con_p1.split(",")[1]
		if req_key == 'empty':
			rcvd_ip = req_key
		else:
			rcvd_ip = str(request.META.get(req_key))
		if con_p1.split(",")[0] == rcvd_ip:
			resp = con_p2.split(",")[0]
			player = 'Player 1'
			resp_p = 'Player 2'
		else:
			resp = con_p1.split(",")[0]
			player = 'Player 2'
			resp_p = 'Player 1'
		action['player'] = player
		con_stat = con[0].connected
		p_turn = str(stat[0].turn)
		if p_turn == '0':
			status.objects.filter(sess_id = sess[0]).update(turn = str(player))
		if p_turn == player and con_stat == True:
			status.objects.filter(sess_id = sess[0]).update(turn = str(resp_p))
			action['turn'] = str(stat[0].turn)
			action['cell_1'] = str(stat[0].cell_1)
			action['cell_2'] = str(stat[0].cell_2)
			action['cell_3'] = str(stat[0].cell_3)
			action['cell_4'] = str(stat[0].cell_4)
			action['cell_5'] = str(stat[0].cell_5)
			action['cell_6'] = str(stat[0].cell_6)
			action['cell_7'] = str(stat[0].cell_7)
			action['cell_8'] = str(stat[0].cell_8)
			action['cell_9'] = str(stat[0].cell_9)
			if con_stat == True:
				action['stat'] = 'Connected'
				status.objects.filter(sess_id = sess[0]).update(game = True)
			else:
				action['stat'] = 'Not Connected'
			if(request.POST.get('1')):
				if stat[0].cell_1 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_1 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_1'] = str(stat[0].cell_1)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_1 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_1'] = str(stat[0].cell_1)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
			
			if(request.POST.get('2')):
				if stat[0].cell_2 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_2 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_2'] = str(stat[0].cell_2)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_2 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_2'] = str(stat[0].cell_2)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('3')):
				if stat[0].cell_3 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_3 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_3'] = str(stat[0].cell_3)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_3 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_3'] = str(stat[0].cell_3)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('4')):
				if stat[0].cell_4 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_4 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_4'] = str(stat[0].cell_4)
						return render(request, "game.html",action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_4 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_4'] = str(stat[0].cell_4)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('5')):
				if stat[0].cell_5 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_5 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_5'] = str(stat[0].cell_5)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_5 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_5'] = str(stat[0].cell_5)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('6')):
				if stat[0].cell_6 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_6 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_6'] = str(stat[0].cell_6)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_6 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_6'] = str(stat[0].cell_6)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('7')):
				if stat[0].cell_7 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_7 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_7'] = str(stat[0].cell_7)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_7 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_7'] = str(stat[0].cell_7)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('8')):
				if stat[0].cell_8 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_8 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_8'] = str(stat[0].cell_8)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_8 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_8'] = str(stat[0].cell_8)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
					
			if(request.POST.get('9')):
				if stat[0].cell_9 == '':
					if player == 'Player 1':
						status.objects.filter(sess_id = sess[0]).update(cell_9 = 'X')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_9'] = str(stat[0].cell_9)
						return render(request, "game.html", action)
					else:
						status.objects.filter(sess_id = sess[0]).update(cell_9 = 'O')
						game_stat = isGameover(sid,player)
						action['gstatus'] = game_stat
						action['cell_9'] = str(stat[0].cell_9)
						return render(request, "game.html", action)
				else:
					# will return something to show invalid move msg
					return render(request, "game.html", action)
			
		else:
			print("invalid turn or not connected")

		return render(request, "game.html", action)
		
	except:
		print("Game Fail")
	
def poll(request):
	poll_dump = {
		'stat' : 'Not Connected',
		'player' : '',
		'sid' : 0,
		'cell_1' : '',
		'cell_2' : '',
		'cell_3' : '',
		'cell_4' : '',
		'cell_5' : '',
		'cell_6' : '',
		'cell_7' : '',
		'cell_8' : '',
		'cell_9' : '',
		'req_stat': False,
		'game_state': '',
		'turn':'',
		'reset': False,
	}
	req_dump = request.GET
	dump = req_dump.dict()
	if dump:
		if dump['sid']:
			sid = dump['sid']
			poll_dump['sid'] = sid
			sess = session.objects.filter(sess_id = str(sid))
			if not sess: 
				poll_dump['game_state'] = str('ac')
				return JsonResponse(poll_dump)

			con = connection.objects.filter(sess_id = sess[0])
			stat = status.objects.filter(sess_id = sess[0])
			player = ''
			con_p1 = con[0].p1
			con_p2 = con[0].p2
			req_key = con_p1.split(",")[1]
			if req_key == 'empty':
				rcvd_ip = req_key
			else:
				rcvd_ip = str(request.META.get(req_key))
			
			if con_p1.split(",")[0] == rcvd_ip:
				resp = con_p2.split(",")[0]
				player = 'Player 1'
			else:
				resp = con_p1.split(",")[0]
				player = 'Player 2'
			
			poll_dump['player'] = player
			con_stat = con[0].connected
			poll_dump['cell_1'] = str(stat[0].cell_1)
			poll_dump['cell_2'] = str(stat[0].cell_2)
			poll_dump['cell_3'] = str(stat[0].cell_3)
			poll_dump['cell_4'] = str(stat[0].cell_4)
			poll_dump['cell_5'] = str(stat[0].cell_5)
			poll_dump['cell_6'] = str(stat[0].cell_6)
			poll_dump['cell_7'] = str(stat[0].cell_7)
			poll_dump['cell_8'] = str(stat[0].cell_8)
			poll_dump['cell_9'] = str(stat[0].cell_9)
			poll_dump['turn'] = str(stat[0].turn)
			poll_dump['game_state'] = str(stat[0].game_state)
			poll_dump['reset'] = str(con[0].reset)
			
			if con_stat == True:
				poll_dump['stat'] = 'Connected'
			else:
				poll_dump['stat'] = 'Not Connected'
			
			poll_dump['req_stat'] = True
			if player == 'Player 2':
				if poll_dump['reset'] == True:
					connection.objects.filter(sess_id = sess[0]).update(reset = False)
					return redirect('/game/')

			return JsonResponse(poll_dump)
		
		else:
			print("request failed")
			return JsonResponse(poll_dump)
	
	else:
		print("page closed")
		return JsonResponse(poll_dump)
		
		
def clear(request):
	req_dump = request.GET
	dump = req_dump.dict()
	if dump:
		if dump['sid']:
			sid = dump['sid']
			ses = session.objects.filter(sess_id = str(sid))
			if ses:
				status.objects.filter(sess_id = ses[0]).update(game = False)
				stat = status.objects.filter(sess_id = ses[0])
				if str(stat[0].game_state) != "cl":
					connection.objects.filter(sess_id = ses[0]).update(timestamp = timezone.now())
					out = session.objects.filter(sess_id = str(sid)).delete()
					if out[0] == 3:
						status.objects.filter(sess_id = ses[0]).update(game_state = "cl")
						return JsonResponse({'game_state' : "cl"})
					else:
						return JsonResponse({'game_state' : "cl"})
				else:
					return JsonResponse({'game_state' : "ac"})
			else:
				#game already closed by another player
				return JsonResponse({'game_state' : "ac"})
				
def getIPaddr(req,sid,plyr):
	try:
		ip = ''
		sess1 = session.objects.filter(sess_id = str(sid))
		con1 = connection.objects.filter(sess_id = sess1[0])
		if con1:
			db_val_p1 = con1[0].p1
		else:
			db_val_p1 = ''
		x_fwd = req.META.get('HTTP_X_FORWARD_FOR')
		addr = req.META.get('REMOTE_ADDR')
		usr_agnt = req.META.get('HTTP_USER_AGENT')
		
		if x_fwd:
			ip = str(x_fwd.split(",")[0]) + ",HTTP_X_FORWARD_FOR"
			if plyr == 'p2':
				if db_val_p1.split(",")[0] != ip.split(",")[0]:
					return ip
				else:
					ip = ''
			else:
				return ip
		
		if addr:
			ip = str(addr) + ",REMOTE_ADDR"
			if plyr == 'p2':
				if db_val_p1.split(",")[0] != ip.split(",")[0]:
					return ip
				else:
					ip = ''
			else:
				return ip
		
		if usr_agnt:
			ip = str(usr_agnt) + ",HTTP_USER_AGENT"
			if plyr == 'p2':
				if db_val_p1.split(",")[0] != ip.split(",")[0]:
					return ip
				else:
					ip = ''
			else:
				return ip
		
		if not ip:
			if plyr == 'p2':
				ip = 'p2,empty'
				return ip
			else:
				ip = 'p1,empty'
				return ip
		
	except:
		print("get ip fail")
		
        
def reset(request):
    sid = request.session['sess_id']
    sess2 = session.objects.filter(sess_id = str(sid))
    sess2[0].delete
    status.objects.filter(sess_id = sess2[0]).update(cell_1 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_2 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_3 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_4 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_5 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_6 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_7 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_8 = '')
    status.objects.filter(sess_id = sess2[0]).update(cell_9 = '')
    status.objects.filter(sess_id = sess2[0]).update(game = True)
    status.objects.filter(sess_id = sess2[0]).update(game_state = '0')
    status.objects.filter(sess_id = sess2[0]).update(turn = '0')
    connection.objects.filter(sess_id = sess2[0]).update(reset = True)
    
    return redirect('/game/')
