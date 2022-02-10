import discord
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from keep_alive import keep_alive 
import datetime
import time
import ast

jsonfile = ast.literal_eval(os.environ['JSON'])
client = gspread.service_account_from_dict(jsonfile)

sheet = client.open("Hours").sheet1
hours=client.open("Hours").worksheet('hours')

#ON FIRST SIGN IN SET PREVIOUS CELLS TO DASHES OR CODE WONT WORK

client = discord.Client()

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith('$signin'):
    await message.delete()
    await message.channel.send('Signed in <@{}>'.format(message.author.id) + " at " + message.created_at.strftime('%H:%M') + " UTC") 
    if str(message.author.id) not in sheet.row_values(1):
      p, l=len(sheet.row_values(1)) + 2, len(hours.row_values(1)) + 1
      sheet.insert_cols([[str(message.author.id),str(message.author)+' Sign In' ], ['', str(message.author)+' Sign Out']], col=p)
      hours.update_cell(2,l, str(message.author)+' Hours worked')
      hours.update_cell(1,l, str(message.author.id))

      if str(message.created_at.strftime('%d/%m/%Y')) not in sheet.col_values(1):
        n, m=len(sheet.col_values(1))+1, len(hours.col_values(1))+1

        dashed = len(sheet.row_values(2))+1

        o=len(sheet.col_values(1))
        b=len(hours.col_values(1))
        last=datetime.datetime.strptime(str(sheet.col_values(1)[o-1]), '%d/%m/%Y')
        lastd=datetime.timedelta(hours=last.day)
        today=message.created_at
        dif=(today-last).days
        zeros=len(hours.row_values(1))+1
        while dif>1:
          o+=1
          b+=1
          val=today - datetime.timedelta(days=(dif-1))
          for x in range (2,dashed):
            sheet.update_cell(o,x, str('-'))
          sheet.update_cell(o,1, val.strftime('%d/%m/%Y'))
          hours.update_cell(b,1, val.strftime('%d/%m/%Y'))
          for k in range(2,zeros):
            hours.update_cell(b,k, '0:00:00')
          n+=1
          m+=1
          dif-=1
        for j in range(2,zeros):
            hours.update_cell(m,j, '0:00:00')

        for x in range (2,dashed):
          sheet.update_cell(n,x, str('-'))
        sheet.update_cell(n,p, str(message.created_at.strftime('%H:%M')))
        sheet.update_cell(n,1, str(message.created_at.strftime('%d/%m/%Y')))
        hours.update_cell(m,1, str(message.created_at.strftime('%d/%m/%Y')))
      else:
        n=sheet.col_values(1).index(str(message.created_at.strftime('%d/%m/%Y')))+1
        sheet.update_cell(n,p, str(message.created_at.strftime('%H:%M')))
        q=hours.col_values(1).index(str(message.created_at.strftime('%d/%m/%Y')))+1
        hours.update_cell(q,l, '0:00:00')


    else:
      i=sheet.row_values(1).index(str(message.author.id)) + 1
      s=hours.row_values(1).index(str(message.author.id)) + 1
      n=len(sheet.col_values(i))+1 
      m=len(hours.col_values(s))+1 
      if str(message.created_at.strftime('%d/%m/%Y')) not in sheet.col_values(1):
        dashed = len(sheet.row_values(2))+1

        o=len(sheet.col_values(1))
        b=len(hours.col_values(1))

        last=datetime.datetime.strptime(str(sheet.col_values(1)[o-1]), '%d/%m/%Y')
        lastd=datetime.timedelta(days=last.day)
        today=message.created_at
        dif=(today-last).days
        zeros=len(hours.row_values(1))+1
        while dif>1:
          o+=1
          b+=1
          val=today - datetime.timedelta(days=(dif-1))
          for x in range (2,dashed):
            sheet.update_cell(o,x, str('-'))
          sheet.update_cell(o,1, val.strftime('%d/%m/%Y'))
          hours.update_cell(b,1, val.strftime('%d/%m/%Y'))
          for k in range(2,zeros):
            hours.update_cell(b,k, '0:00:00')
          n+=1
          m+=1
          dif-=1
        for j in range(2,zeros):
            hours.update_cell(m,j, '0:00:00')

        for x in range (2,dashed):
            sheet.update_cell(n,x, str('-'))
        sheet.update_cell(n,i, str(message.created_at.strftime('%H:%M')))
        sheet.update_cell(n,1, str(message.created_at.strftime('%d/%m/%Y')))
        hours.update_cell(m,1, str(message.created_at.strftime('%d/%m/%Y')))
      else:
        dashed = len(sheet.row_values(2))+1
        p=sheet.col_values(1).index(str(message.created_at.strftime('%d/%m/%Y')))+1
        if str(sheet.cell(p,i).value) != '-':
          for x in range (2,dashed):
            sheet.update_cell(p+1,x, str('-'))
          sheet.update_cell(p+1,1, str(message.created_at.strftime('%d/%m/%Y')))
          sheet.update_cell(p+1,i, str(message.created_at.strftime('%H:%M')))
        else:
          sheet.update_cell(p,i, str(message.created_at.strftime('%H:%M')))
      
  if message.content.startswith('$signout'):
    await message.delete()
    await message.channel.send('Signed out <@{}>'.format(message.author.id) + " at " + message.created_at.strftime('%H:%M') + " UTC") 
    p=hours.col_values(1).index(str(message.created_at.strftime('%d/%m/%Y')))+1
    l=hours.row_values(1).index(str(message.author.id))+1
    n=sheet.col_values(1).index(str(message.created_at.strftime('%d/%m/%Y')))+1
    m=sheet.row_values(1).index(str(message.author.id))+2
    if str(hours.cell(p,l).value) == "0:00:00":
      sheet.update_cell(n,m, str(message.created_at.strftime('%H:%M')))
      t1=datetime.datetime.strptime(str(sheet.cell(n,m).value), '%H:%M')
      t2=datetime.datetime.strptime(str(sheet.cell(n,m-1).value), '%H:%M')
      hours.update_cell(p,l, str(t1-t2))
    else:
      n+=1
      sheet.update_cell(n,m, str(message.created_at.strftime('%H:%M')))
      t1=datetime.datetime.strptime(str(sheet.cell(n,m).value), '%H:%M')
      t2=datetime.datetime.strptime(str(sheet.cell(n,m-1).value), '%H:%M')
      newtime=datetime.datetime.strptime(str(hours.cell(p,l).value), '%H:%M:%S')
      newtime=datetime.timedelta(hours=newtime.hour, minutes=newtime.minute)
      hours.update_cell(p,l, str(newtime + t1 -t2))

  if message.content.startswith('$week'):
    n=len(sheet.col_values(1))-1
    start, end, ref = '1','2', 0
    while True:
      date=str(sheet.col_values(1)[n]).split('/')
      date=' '.join([str(elem) for elem in date])
      day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday'] 
      day = datetime.datetime.strptime(date, '%d %m %Y').weekday()
      if str(day_name[day]) != 'Friday':
        n -= 1
      else:
        end=str(sheet.col_values(1)[n])
        ref=n 
        break
    while True:
      date=str(sheet.col_values(1)[ref]).split('/')
      date=' '.join([str(elem) for elem in date])
      day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday'] 
      day = datetime.datetime.strptime(date, '%d %m %Y').weekday()
      if str(day_name[day]) != 'Sunday':
        ref -= 1
      else:
        start=str(sheet.col_values(1)[ref+1])
        break

    n=hours.col_values(1).index(str(start))+1
    d1=datetime.datetime.strptime(str(hours.cell(n,2).value), '%H:%M:%S')
    add=datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
    for i in range(1,7): 
      if hours.cell(n+i,2).value:
        d1=datetime.datetime.strptime(str(hours.cell(n+i,2).value), '%H:%M:%S')
        add+=datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
    timed=round(add.days *24 + add.seconds/3600, 2)
    await message.channel.send('<@{}>'.format(message.author.id) + " worked " + str(timed) + " hours last week.") 

  if message.content.startswith('$commands'):
    embed = discord.Embed(
      title = 'Commands',
      description = '',
      colour= discord.Colour.blue()
    )
    embed.set_footer(text = 'Created by <@{}>'.format('sonarize#7379'))
    embed.add_field(name='$signin', value='Sign in on the Google sheet.', inline=False)
    embed.add_field(name='$signout', value='Sign out on the Google sheet.', inline=False)
    embed.add_field(name='$week', value='See your hours worked from the previous week.', inline=False)
    embed.add_field(name='$sheet', value='Google sheet link. All times are in UTC', inline=False)
    embed.add_field(name='$allhours', value='Shows how many hours everyone has worked since the beginning', inline=False)
    await message.channel.send(embed=embed)

  if message.content.startswith('$sheet'):
    await message.channel.send("https://docs.google.com/spreadsheets/d/1Q2OXJCGWVWlioy3aSiVAT7rIg-J9lQkSSjEvK9BipMc/edit?usp=sharing")
  
  if message.content.startswith('$allhours'):
    embeddict={}
    for j in range(2,len(hours.row_values(2))+1):
      addtime1=datetime.timedelta(hours=0, minutes=0, seconds=0)
      columns=hours.col_values(j)
      for i in range(2,len(columns)):
        if str(columns[i]) != '':
          time1=datetime.datetime.strptime(str(columns[i]), '%H:%M:%S')
          addtime1+=datetime.timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second)
      time1hours=round(addtime1.days *24 + addtime1.seconds/3600, 2)
      embeddict[hours.row_values(2)[j-1]]=time1hours
    embed2 = discord.Embed(
        title = 'Hours worked since the beginning',
        description = '',
        colour= discord.Colour.blue()
      )
    embed2.set_footer(text = 'Created by <@{}>'.format('sonarize#7379'))
    for key, value in embeddict.items() :
      embed2.add_field(name=key, value=value, inline=False)
    await message.channel.send(embed=embed2)
      

keep_alive()
client.run(os.environ['TOKEN'])