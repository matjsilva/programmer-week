from github import *
from datetime import date, datetime

today = datetime.today()
g = Github("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")
points = 0
users = ['F1NH4WK', 'WasixXD', 'matjsilva']
ranking = {}

try:
    for user in users:
        for repo in g.get_user(user).get_repos():
            try:
                if repo.pushed_at.day <= today.day and repo.pushed_at.month == today.month and repo.pushed_at.year == today.year:
                    last = repo.get_stats_code_frequency()[len(repo.get_stats_code_frequency())-1]

                    if last.additions == 0 and last.deletions == 0:
                        pass
                    else:
                        print(f"\nVerificando repositório {repo.name} | Verificando a partir de: {last.week} (semana mais recente)\n")
                        print(f"Adições no repositório {repo.name}: {last.additions}")
                        print(f"Deletes no repositório {repo.name}: {last.deletions}")
                        points += abs(last.additions)
                        points += abs(last.deletions)
                else:
                    pass
            except:
                print(f"O repositório {repo.name} do usuário {user} está vazio.")
                continue
        print(f"\n\nTotal de mudanças {user}: {points}")
        ranking[user] = points
        points = 0
except:
    print(f"O usuário {user} não existe.")

print("\n\n")

finalScore = dict(sorted(ranking.items(), reverse=True, key=lambda item: item[1]))
weekProgrammer = ""
i = 1

for score in finalScore:
    print(f"{i}. {score} - {finalScore[score]}")
    if i == 1:
        weekProgrammer = score
    i += 1

print(f"Programador da semana: {weekProgrammer}")
