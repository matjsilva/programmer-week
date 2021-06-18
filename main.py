import discord, asyncio, os, json
from discord import embeds
from github import *
from discord.ext import commands, tasks
from datetime import date, datetime

client = commands.Bot(command_prefix = 'p?', case_insensitive=True, help_command=None)

usersAllowed = [308008129939898378, 842718415403483166]
usersAllowedFormated = []
for user in usersAllowed:
    usersAllowedFormated.append(f'<@{user}>')

with open("secrets.json") as s:
    dataSecrets = json.load(s)

weekProgrammer = ""
thisWeek = None
timeToNextCheck = 0

g = Github(dataSecrets['github'])

@client.event
async def on_ready():
    print(f"[{datetime.today()}] {client.user.name} ligado! (id = {client.user.id})")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Repositórios [build: cloud]"))
    print("======-======\n")

@tasks.loop(seconds = 5)
async def rankCheck():
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
                        last = repo.get_stats_code_frequency()[len(repo.get_stats_code_frequency())-1]
                        
                        if today.day == last.week.day+7:
                            rankFinal()

                        if repo.pushed_at.day <= today.day and repo.pushed_at.month == today.month and repo.pushed_at.year == today.year:
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
                try:
                    last = repo.get_stats_code_frequency()[len(repo.get_stats_code_frequency())-1]

                    if today.day == last.week.day+7:
                        rankFinal()

                    if repo.updated_at.day == today.day and repo.updated_at.month == today.month and repo.updated_at.year == today.year and repo.updated_at.hour == today.hour and repo.updated_at.min == today.min and today.second - repo.updated_at.second <= 5:
                        if last.additions == 0 and last.deletions == 0:
                            pass
                        else:
                            dataPlayer[player]['points'] += abs(last.additions)
                            dataPlayer[player]['points'] += abs(last.deletions)
                    else:
                        pass
                except:
                    print(f"O repositório {repo.name} do usuário {dataPlayer[player]['github']} não possui atualizações recentes.")
    except:
        print(f"O usuário {dataPlayer[player]['discord']} não existe, ou o usuário {dataPlayer[player]['github']} não existe.")

    finalRanking = dict(sorted(data['pointRanking'].items(), reverse=True, key=lambda item: item[1]))
    if len(data['pointRanking'].items()) >= 3:
        i = 1

        for ranked in finalRanking:
            for playerFix in dataPlayer:
                if dataPlayer[playerFix]['github'] == ranked:
                    player = playerFix

            if dataPlayer[player]["hasVerifiedThisWeek"] == 0:
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
async def help(ctx, comando=""):
    defaultEmbed = discord.Embed(
        title="Ajuda **Semana do Programador**",
        description = "Lista de comandos do Bot!"
    )
    defaultEmbed.add_field(name="p?entrar", value="Use para entrar na **Semana do Programador**.", inline=False)
    defaultEmbed.add_field(name="p?rank", value="Use para ver a Leaderboard da semana.", inline=False)
    defaultEmbed.add_field(name="p?perfil @usuario (obrigatório)", value="Use para ver o seu perfil ou o perfil de outra pessoa", inline=False)
    defaultEmbed.add_field(name="p?ligas", value="Use para ver os usuários com maior rank do servidor!", inline=False)
    defaultEmbed.add_field(name="p?help ranks", value="Explica o sistema de ranks", inline=False)
    defaultEmbed.add_field(name="p?help entrar", value="Explica o comando p?entrar", inline=False)
    defaultEmbed.add_field(name="p?help rank", value="Explica a Leaderboard da semana.", inline=False)
    defaultEmbed.add_field(name="p?help perfil", value="Explica o comando p?perfil", inline=False)
    defaultEmbed.add_field(name="p?help ligas", value="Explica o comando p?ligas e o sistema de Ligas", inline=False)

    entrarEmbed = discord.Embed(
        title="p?entrar",
        description = "Usado para ingressar na **Semana do Programador**, uma vez usado, não será mais necessário se inscrever."
    )

    rankEmbed = discord.Embed(
        title="p?rank",
        description="Usado para ver a Leaderboard da semana. A Leaderboard pode mudar conforme mais pessoas ingressam, caso essa pessoa tenha mais pontos que o resto, ela sobe, mesmo que haja um 1º lugar anteriormente."
    )

    perfilEmbed = discord.Embed(
        title="p?perfil @usuario",
        description="Usado para ver o perfil do usuário mencionado. (é necessário mencionar, mesmo que seja você mesmo)",
    )

    ranksEmbed = discord.Embed(
        title="Sistema de Ranks",
        description="O sistema de ranks permite destacar os programadores mais ativos do servidor e encoraja o desenvolvimento de projetos de programação!"
    )

    ligasEmbed = discord.Embed(
        title="p?ligas | Sistema de Ligas",
        description = "Diferente do Rank da **Semana do Programador**, a Liga é permanente e o programador mais resiliente irá se classificar aos elos mais altos."
    )

    if comando == "":
        await ctx.send(embed = defaultEmbed)
    elif comando == "entrar":
        await ctx.send(embed = entrarEmbed)
    elif comando == "rank":
        await ctx.send(embed = rankEmbed)
    elif comando == "perfil":
        await ctx.send(embed = perfilEmbed)
    elif comando == "ranks":
        await ctx.send(embed = ranksEmbed)
    elif comando == "ligas":
        await ctx.send(embed = ligasEmbed)
    else:
        await ctx.send(embed = defaultEmbed)

@client.command()
async def checar(ctx):
    if ctx.author.id in usersAllowed:
        rankCheck()
    else:
        alert = f"""
:exclamation:<@{ctx.author.id}>, você não tem permissão para usar este comando!:exclamation:

As pessoas que podem realizar uma checagem manual são: {', '.join(usersAllowedFormated)}
        """
        await ctx.send(alert)

@client.command()
async def ligas(ctx):
    with open("players.json", encoding='utf-8') as p:
        dataPlayer = json.load(p)

    leagueRanks = {
        "<:iniciante:854698137029836820>": [],
        "<:amador:854698137607733268>": [],
        "<:experiente:854698137934233630>": [],
        "<:campeao:854698137653739550>": [],
        "<:lenda:854698137691226112>": []
    }

    for player in dataPlayer:
        if dataPlayer[player]['title'] == "Iniciante":
            leagueRanks["<:iniciante:854698137029836820>"].append(dataPlayer[player]['discord'])
        elif dataPlayer[player]['title'] == "Amador":
            leagueRanks["<:amador:854698137607733268>"].append(dataPlayer[player]['discord'])
        elif dataPlayer[player]['title'] == "Experiente":
            leagueRanks["<:experiente:854698137934233630>"].append(dataPlayer[player]['discord'])
        elif dataPlayer[player]['title'] == "Campeão":
            leagueRanks["<:campeao:854698137653739550>"].append(dataPlayer[player]['discord'])
        elif dataPlayer[player]['title'] == "Lenda":
            leagueRanks["<:lenda:854698137691226112>"].append(dataPlayer[player]['discord'])

    thisEmbed = discord.Embed(
        title="Ligas da Semana do Programador",
        description="Suba de liga e torne-se o melhor programador!"
    )

    if len(leagueRanks['<:lenda:854698137691226112>']) >= 1:
        thisEmbed.add_field(name="<:lenda:854698137691226112> **Lenda**", value=", ".join(leagueRanks['<:lenda:854698137691226112>']), inline=False)
    else:
        thisEmbed.add_field(name="<:lenda:854698137691226112> **Lenda**", value='Não há jogadores nesta liga.', inline=False)

    if len(leagueRanks['<:campeao:854698137653739550>']) >= 1:
        thisEmbed.add_field(name="<:campeao:854698137653739550> **Campeão**", value=", ".join(leagueRanks['<:campeao:854698137653739550>']), inline=False)
    else:
        thisEmbed.add_field(name="<:campeao:854698137653739550> **Campeão**", value='Não há jogadores nesta liga.', inline=False)

    if len(leagueRanks['<:experiente:854698137934233630>']) >= 1:
        thisEmbed.add_field(name="<:experiente:854698137934233630> **Experiente**", value=", ".join(leagueRanks['<:experiente:854698137934233630>']), inline=False)
    else:
        thisEmbed.add_field(name="<:experiente:854698137934233630> **Experiente**", value='Não há jogadores nesta liga.', inline=False)

    if len(leagueRanks['<:amador:854698137607733268>']) >= 1:
        thisEmbed.add_field(name="<:amador:854698137607733268> **Amador**", value=", ".join(leagueRanks['<:amador:854698137607733268>']), inline=False)
    else:
        thisEmbed.add_field(name="<:amador:854698137607733268> **Amador**", value='Não há jogadores nesta liga.', inline=False)

    if len(leagueRanks['<:iniciante:854698137029836820>']) >= 1:
        thisEmbed.add_field(name="<:iniciante:854698137029836820> **Iniciante**", value=", ".join(leagueRanks['<:iniciante:854698137029836820>']), inline=False)
    else:
        thisEmbed.add_field(name="<:iniciante:854698137029836820> **Iniciante**", value='Não há jogadores nesta liga.', inline=False)
    thisEmbed.set_footer(text="Preparado para subir de liga?")

    await ctx.send(embed = thisEmbed)

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

        embed.add_field(name="Loop atual do rankCheck", value=rankCheck.current_loop, inline=False)
        embed.add_field(name="Próximo loop do rankCheck", value=rankCheck.next_iteration, inline=False)
        embed.add_field(name="Intervalo do loop (segundos)", value=rankCheck.seconds, inline=False)

        embed.set_thumbnail(url='https://i.pinimg.com/originals/0c/67/5a/0c675a8e1061478d2b7b21b330093444.gif')

        await ctx.send(embed = embed)
    else:
        alert = f"""
:exclamation:<@{ctx.author.id}>, você não tem permissão para usar este comando!:exclamation:

As pessoas que podem visualizar meus dados são: {', '.join(usersAllowedFormated)}
        """
        await ctx.send(alert)
    
    d.close()

@client.command()
async def entrar(ctx, github=""):
    with open("players.json", encoding='utf-8') as wp:
        dataPlayer = json.load(wp)

        who = ctx.author
    
    if github == "":
        alert = f"""
:arrow_right: <@{ctx.author.id}>, para te inscrever na próxima **Semana do Programador**, vou precisar do seu usuário no Github!

Uso correto deste comando:
```p?entrar meuUsuarioNoGithub```
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
```p?entrar meuUsuarioNoGithub```
"""
            await ctx.send(alert)
            return
    
    confirmed = f"""
:partying_face: Parabéns! Você foi inscrito na próxima **Semana do Programador**, continue produzindo! Use p?rank para checar seu **rank**!.
"""

    if who.id in dataPlayer:
        await ctx.send(":exclamation:Você já está inscrito na **Semana do Programador**!")
        return
    else:
        for player in dataPlayer:
            if dataPlayer[player]['github'] == github:
                await ctx.send(f":exclamation:Você já está inscrito na **Semana do Programador**! => <@{player}> - {dataPlayer[player]['github']}")
                return

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

        for player in dataPlayer:
            if dataPlayer[player]['github'] == data['ranking']['1']:
                first = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['2']:
                second = f"{player}"
            elif dataPlayer[player]['github'] == data['ranking']['3']:
                third = f"{player}"

        embed = discord.Embed(
            title=f"Leaderboard | Semana em andamento...",
            description="Os programadores mais ativos do servidor costumam se destacar nessa lista."
        )
            
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

    with open('data.json', encoding='utf-8') as d:
        data = json.load(d)

    with open('players.json', encoding='utf-8') as p:
        dataPlayer = json.load(p)

    try:
        others = []
        first = ""
        second = ""
        third = ""

        embed = discord.Embed(
            title=f"Leaderboard | Programador da semana = {dataPlayer[first]['discord']}",
            description=f"O grande ganhador desta **Semana do Programador** é {dataPlayer[first]['discord']}!"
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

        dataPlayer[first]['titles'] += 1
        if dataPlayer[first]['titles'] in data['titles']['Amador']:
            dataPlayer[first]['title'] = 'Amador'
        elif dataPlayer[first]['titles'] in data['titles']['Experiente']:
            dataPlayer[first]['title'] = 'Experiente'
        elif dataPlayer[first]['titles'] in data['titles']['Campeão']:
            dataPlayer[first]['title'] = 'Campeão'
        elif dataPlayer[first]['titles'] > data['titles']['Lenda']:
            dataPlayer[first]['title'] = 'Lenda'

        for ranked in data['ranking']:
            if ranked != "1" and ranked != "2" and ranked != "3":
                others.append(data['ranking'][ranked])

        if len(others) >= 1: 
            embed.add_field(name="Outras colocações (parabéns!)", value=f", ".join(others))

        embed.set_footer(text="Os 3 programadores mais ativos da semana!")

        for player in dataPlayer:
            dataPlayer[player]["hasVerifiedThisWeek"] = 0
            dataPlayer[player]["points"] = 0

        data['ranking'] = {}
        data['pointRanking'] = {}
        
        with open('players.json', encoding='utf-8') as wp:
            json.dump(dataPlayer, wp, indent=4)

        with open('data.json', encoding='utf-8') as wd:
            json.dump(data, wd, indent=4)

        await ctx.send("@everyone A **Semana do Programador** chegou ao fim! Aqui estão os 3 primeiros colocados da leaderboard:smiley:")
        await ctx.send(embed = embed)
    except:
        await ctx.send(":confused:Não tivemos programadores o suficiente para organizar uma leaderboard esta semana, que tal compartilhar a **Semana do Programador** para um amigo?")

    d.close()
    p.close()

@client.command()
async def perfil(ctx, user: discord.User):
    with open("players.json", 'r', encoding='utf-8') as d:
        data = json.load(d)

    try:
        if user == "" or user == " ":
            user = ctx.author

        if str(user.id) in data:
            embed = discord.Embed(
                title = f"{user} | {data[str(user.id)]['github']}",
                description = g.get_user(data[str(user.id)]['github']).bio
            )

            langs = {}
            for repo in g.get_user(data[str(user.id)]['github']).get_repos():
                if repo.language in langs:
                    langs[repo.language] += repo.get_languages()[repo.language]
                elif repo.language == None:
                    pass
                else:
                    langs[repo.language] = repo.get_languages()[repo.language]
            
            mostUsed = sorted(langs.items(), reverse=True, key=lambda item: item[1])

            embed.set_thumbnail(url=user.avatar_url)

            embed.add_field(name='Github', value=data[str(user.id)]['github'], inline=True)
            embed.add_field(name='Linguagem Favorita', value=mostUsed[0][0], inline=True)
            embed.add_field(name='Títulos', value=data[str(user.id)]['titles'], inline=False)

            if data[str(user.id)]['title'] == "Iniciante":
                embed.add_field(name='Rank', value=f"<:iniciante:854698137029836820> {data[str(user.id)]['title']}", inline=False)
            elif data[str(user.id)]['title'] == "Amador":
                embed.add_field(name='Rank', value=f"<:amador:854698137607733268> {data[str(user.id)]['title']}", inline=False)
            elif data[str(user.id)]['title'] == "Experiente":
                embed.add_field(name='Rank', value=f"<:experiente:854698137934233630> {data[str(user.id)]['title']}", inline=False)
            elif data[str(user.id)]['title'] == "Campeão":
                embed.add_field(name='Rank', value=f"<:campeao:854698137653739550> {data[str(user.id)]['title']}", inline=False)
            elif data[str(user.id)]['title'] == "Lenda":
                embed.add_field(name='Rank', value=f"<:lenda:854698137691226112> {data[str(user.id)]['title']}", inline=False)

            await ctx.send(embed = embed)

            d.close()
        else:
            await ctx.send("""
:confused: Você ainda não se inscreveu na Semana do Programador, que tal se inscrever agora?

Se inscreva usando o comando:
```p?entrar meuUsuarioNoGithub```
    """)
    except Exception:
        raise

    d.close()

rankCheck.start()
client.run(dataSecrets['token'])
s.close()