import discord, asyncio, os, json
from github import *
from discord.ext import commands
from datetime import date, datetime

client = commands.Bot(command_prefix = 'p?', case_insensitive=True)

usersAllowed = [308008129939898378, 842718415403483166]
usersAllowedFormated = []
for user in usersAllowed:
    usersAllowedFormated.append(f'<@{user}>')

with open("secrets.json") as s:
    dataSecrets = json.load(s)

weekProgrammer = ""
thisWeek = None

g = Github(dataSecrets['github'])

@client.event
async def on_ready():
    print(f"[{datetime.today()}] {client.user.name} ligado! (id = {client.user.id})")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Repositórios"))
    print("======-======\n")

def rankCheck():
    global weekProgrammer, thisWeek

    with open("data.json", 'r', encoding='utf-8') as d:
        data = json.load(d)

    with open("players.json", 'r', encoding='utf-8') as p:
        dataPlayer = json.load(p)

    today = datetime.today()

    try:
        for player in dataPlayer:
            if dataPlayer[player]['hasVerifiedThisWeek'] == 0:
                for repo in g.get_user(dataPlayer[player]['github']).get_repos():
                    try:
                        if today.day - repo.pushed_at.day == 0:
                            rankFinal()

                        if repo.pushed_at.day <= today.day and repo.pushed_at.month == today.month and repo.pushed_at.year == today.year:
                            last = repo.get_stats_code_frequency()[len(repo.get_stats_code_frequency())-1]
                            thisWeek = last

                            if last.additions == 0 and last.deletions == 0:
                                pass
                            else:
                                dataPlayer[player]['points'] += abs(last.additions)
                                dataPlayer[player]['points'] += abs(last.deletions)
                        else:
                            pass
                    except:
                        print(f"O repositório {repo.name} do usuário {dataPlayer[player]['github']} está vazio.")
                        continue
                data['pointRanking'][dataPlayer[player]['github']] = dataPlayer[player]['points']
            else: 
                pass
    except:
        print(f"O usuário {player} não existe.")

    finalRanking = dict(sorted(data['pointRanking'].items(), reverse=True, key=lambda item: item[1]))
    if len(data['pointRanking'].items()) >= 3:
        i = 1

        for ranked in finalRanking:
            for playerFix in dataPlayer:
                if dataPlayer[playerFix]['github'] == ranked:
                    player = playerFix

            if dataPlayer[player]["hasVerifiedThisWeek"] == 0:
                if i == 1:
                    weekProgrammer = ranked 

                    for playerFixToo in dataPlayer:
                        if dataPlayer[playerFixToo]['github'] == ranked:
                            dataPlayer[playerFixToo]['titles'] += 1

                            if dataPlayer[playerFixToo]['titles'] in data['titles']['Amador']:
                                dataPlayer[playerFixToo]['title'] = 'Amador'
                            elif dataPlayer[playerFixToo]['titles'] in data['titles']['Experiente']:
                                dataPlayer[playerFixToo]['title'] = 'Amador'
                            elif dataPlayer[playerFixToo]['titles'] in data['titles']['Campeão']:
                                dataPlayer[playerFixToo]['title'] = 'Amador'
                            elif dataPlayer[playerFixToo]['titles'] > data['titles']['Lenda']:
                                dataPlayer[playerFixToo]['title'] = 'Amador'
                data['ranking'][i] = dataPlayer[player]['github']
            dataPlayer[player]['hasVerifiedThisWeek'] = 1
            i += 1

    with open('data.json', 'w', encoding='utf-8') as wd:
        json.dump(data, wd, indent=4)
    with open('players.json', 'w', encoding='utf-8') as wp:
        json.dump(dataPlayer, wp, indent=4)

    wd.close()
    wp.close()
    d.close()
    p.close()

@client.command()
async def ping(ctx):
    await ctx.send("pong! :sunglasses:")

@client.command()
async def ajuda(ctx, comando=""):
    if comando == "":
        pass
    elif comando == "entrar":
        pass
    elif comando == "rank":
        pass
    elif comando == "perfil":
        pass
    else:
        pass

@client.command()
async def checar(ctx):
    rankCheck()

@client.command()
async def dados(ctx):
    with open("data.json", encoding='utf-8') as d:
        data = json.load(d)

    with open("players.json", encoding='utf-8') as p:
        dataPlayer = json.load(p)

    if ctx.author.id in usersAllowed:
        embed = discord.Embed(
            title = "Programador da Semana",
            description = "Dados do BOT da Semana do Programador."
        )

        embed.set_author(name=ctx.author, icon_url='https://image.flaticon.com/icons/png/512/1465/1465611.png')

        embed.set_footer(text=f"Dados coletados em: {datetime.today().day} do {datetime.today().date().month} de {datetime.today().year}, às {datetime.today().hour} horas e {datetime.today().minute} minutos.")

        if len(dataPlayer) == 0:
            embed.add_field(name='Usuários Inscritos', value='Não há nenhum usuário inscrito.', inline=False)
        else:
            players = []
            for player in dataPlayer:
                players.append(f'<@{int(player)}>')

            embed.add_field(name='Usuários Inscritos', value=', '.join(players), inline=False)

        embed.set_thumbnail(url='https://i.pinimg.com/originals/0c/67/5a/0c675a8e1061478d2b7b21b330093444.gif')

        await ctx.send(embed = embed)
    else:
        alert = f"""
:exclamation:<@{ctx.author.id}>, você não tem permissão para gerenciar este evento!:exclamation:

As pessoas que podem gerenciar meus eventos são: {', '.join(usersAllowedFormated)}
        """
        await ctx.send(alert)
    
    d.close()

@client.command()
async def entrar(ctx, github="", who=""):
    with open("players.json", encoding='utf-8') as wp:
        dataPlayer = json.load(wp)

    if who == "":
        who = ctx.author
    
    if github == "":
        alert = f"""
:arrow_right: <@{ctx.author.id}>, para te inscrever na próxima **Semana do Programador**, vou precisar do seu usuário no Github!

Uso correto deste comando:
```p?entrar meuUsuarioNoGithub usuarioNoDiscord(opcional)```
"""
        await ctx.send(alert)
        return
    else:
        try:
            g.get_user(github)
        except:
            alert = f"""
:arrow_right: <@{ctx.author.id}>, o usuário do Github informado não existe!

Uso correto deste comando:
```p?entrar meuUsuarioNoGithub usuarioNoDiscord(opcional)```
"""
            await ctx.send(alert)
            return
    
    confirmed = f"""
:partying_face: Parabéns! Você foi inscrito na próxima **Semana do Programador**, continue produzindo! Use `p?rank` para checar seu **rank**!.
"""

    if str(who.id) in dataPlayer:
        await ctx.send(":exclamation:Você já está inscrito na **Semana do Programador**!")
        return
    else:
        thisUserData = {
            "github": "github",
            "titles": 0,
            "title": "Iniciante",
            "points": 0,
            "discord": "",
            "hasVerifiedThisWeek": 0
        }

        thisUserData['github'] = github
        thisUserData['titles'] = 0
        thisUserData['title'] = "Iniciante"
        thisUserData['discord'] = str(ctx.author)
        thisUserData['hasVerifiedThisWeek'] = 0

        dataPlayer[who.id] = thisUserData

        with open('players.json', 'w', encoding='utf-8') as fp:
            json.dump(dataPlayer, fp, indent=4)

        wp.close()
        fp.close()

        rankCheck()

        await ctx.send(confirmed)

@client.command()
async def rank(ctx):
    global thisWeek

    with open('data.json', 'r', encoding='utf-8') as d:
        data = json.load(d)

    with open('players.json', 'r', encoding='utf-8') as p:
        dataPlayer = json.load(p)

    try:
        others = []
        first = ""
        second = ""
        third = ""

        embed = discord.Embed(
            name=f"Leaderboard | Semana {thisWeek}",
            description="Os programadores mais ativos do servidor costumam se destacar nessa lista."
        )

        for player in dataPlayer:
            if dataPlayer[player]['github'] == data['ranking']['1']:
                first = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['2']:
                second = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['3']:
                third = f"{player}"
            
        embed.add_field(name=f":first_place:Primeiro Lugar - {data['ranking']['1']} ({dataPlayer[first]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['1']]} | Títulos: {dataPlayer[first]['titles']}", inline=False)
        embed.add_field(name=f":second_place:Segundo Lugar - {data['ranking']['2']} ({dataPlayer[second]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['2']]} | Títulos: {dataPlayer[second]['titles']}", inline=False)
        embed.add_field(name=f":third_place:Terceiro Lugar - {data['ranking']['3']} ({dataPlayer[third]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['3']]} | Títulos: {dataPlayer[third]['titles']}", inline=False)

        for ranked in data['ranking']:
            if ranked != "1" and ranked != "2" and ranked != "3":
                others.append(data['ranking'][ranked])

        if len(others) >= 1: 
            embed.add_field(name="Outras colocações (parabéns!)", value=f", ".join(others))

        embed.set_footer(text="Os 3 programadores mais ativos da semana!")

        await ctx.send(embed = embed)
    except:
        await ctx.send(":hourglass: Os resultados ainda estão sendo computados, ou não há jogadores o suficiente para preencher a leaderboard, aguarde mais um pouco!")

    d.close()
    p.close()

@client.command()
async def rankFinal(ctx):
    global thisWeek

    with open('data.json', 'r', encoding='utf-8') as d:
        data = json.load(d)

    with open('players.json', encoding='utf-8') as p:
        dataPlayer = json.load(p)

    try:
        others = []
        first = ""
        second = ""
        third = ""

        embed = discord.Embed(
            name=f"Leaderboard | Semana {thisWeek}",
            description="Os programadores mais ativos do servidor costumam se destacar nessa lista."
        )

        for player in dataPlayer:
            if dataPlayer[player]['github'] == data['ranking']['1']:
                first = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['2']:
                second = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['3']:
                third = f"{player}"
            
        embed.add_field(name=f":first_place:Primeiro Lugar - {data['ranking']['1']} ({dataPlayer[first]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['1']]} | Títulos: {dataPlayer[first]['titles']}", inline=False)
        embed.add_field(name=f":second_place:Segundo Lugar - {data['ranking']['2']} ({dataPlayer[second]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['2']]} | Títulos: {dataPlayer[second]['titles']}", inline=False)
        embed.add_field(name=f":third_place:Terceiro Lugar - {data['ranking']['3']} ({dataPlayer[third]['discord']})", value=f"Pontos: {data['pointRanking'][data['ranking']['3']]} | Títulos: {dataPlayer[third]['titles']}", inline=False)

        for ranked in data['ranking']:
            if ranked != "1" and ranked != "2" and ranked != "3":
                others.append(data['ranking'][ranked])

        if len(others) >= 1: 
            embed.add_field(name="Outras colocações (parabéns!)", value=f", ".join(others))

        embed.set_footer(text="Os 3 programadores mais ativos da semana!")

        for player in dataPlayer:
            dataPlayer[player]["hasVerifiedThisWeek"] = 0
            dataPlayer[player]["points"] = 0
        
        with open('players.json', encoding='utf-8') as wp:
            json.dump(dataPlayer, wp, indent=4)

        await ctx.send("@everyone A **Semana do Programador** chegou ao fim! Aqui estão os 3 primeiros colocados da leaderboard:smiley:")
        await ctx.send(embed = embed)
    except:
        await ctx.send(":confused:Não tivemos programadores o suficiente para organizar uma leaderboard esta semana, que tal compartilhar a **Semana do Programador** para um amigo?")

    d.close()
    p.close()

@client.command()
async def perfil(ctx):
    with open("players.json", 'r', encoding='utf-8') as d:
        data = json.load(d)

    if str(ctx.author.id) in data:
        embed = discord.Embed(
            title = f"Dados de {ctx.author}",
            description = "Alguns dados sobre você."
        )

        embed.set_thumbnail(url=ctx.author.avatar_url)

        embed.add_field(name='Github', value=data[str(ctx.author.id)]['github'], inline=False)
        embed.add_field(name='Títulos', value=data[str(ctx.author.id)]['titles'], inline=False)
        embed.add_field(name='Rank', value=data[str(ctx.author.id)]['title'], inline=False)

        await ctx.send(embed = embed)
    else:
        await ctx.send("""
:confused: Você ainda não se inscreveu na Semana do Programador, que tal se inscrever agora?

Se inscreva usando o comando:
```p?entrar meuUsuarioNoGithub usuarioNoDiscord(opcional)```
""")

    d.close()

client.run(dataSecrets['token'])
s.close()