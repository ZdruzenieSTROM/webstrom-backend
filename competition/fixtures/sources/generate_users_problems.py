import json
import random

#######################################
current_registration_id = 0
current_solution_id = 0
schools = ["000598071", "000160997", "000160971", "017337101",
           "037956230", "710261519", "017080720", "710234341"]
#######################################

# TODO: upraviť na nový User Model


def generate_user(pk):
    return {
        "model": "user.user",
        "pk": pk,
        "fields": {
            "password":
                "pbkdf2_sha256$180000$UQCtl76TyAYT$y7KcapcAcpnZ5P2cOP75RnzM9dsZAFPGSwsFvzG+YsA=",
            "last_login": "2020-04-07T21:00:28.430Z",
            "date_joined": "2020-04-07T20:43:01.351Z",
            "is_superuser": False,
            "email": f'riesitel{pk}@strom.sk',
            "verified_email": True,
            "is_staff": True,
            "is_active": True,
            "groups": [],
            "user_permissions": []
        }
    }


def generate_profile(pk, user, year, school):
    return {
        "model": "user.profile",
        "pk": pk,
        "fields": {
            "user": user,
            "first_name": "Ucastnik ",
            "last_name": f'Priezvisko{user}',
            "nickname": f'Prezyvka{user}',
            "school": "000160997",
            "year_of_graduation": year,
            "phone": "+421912345678",
            "parent_phone": "+421912345678"
        }
    }


def generate_event_reg(user, school, grade, event):
    global current_registration_id
    d = {
        "model": "competition.UserEventRegistration",
        "pk": current_registration_id,
        "fields": {
            "user": user,
            "school": school,
            "class_level": grade,
            "event": event
        }
    }
    current_registration_id += 1
    return d, current_registration_id-1


def generate_solution(eventreg_pk, problem, points=None):
    global current_solution_id
    d = {
        "model": "competition.Solution",
        "pk": current_solution_id,
        "fields": {
            "user_semester_registration": eventreg_pk,
            "problem": problem,
            "score": points,
            "uploaded_at": "2020-04-01T20:00:00.000Z",
            "is_online": False
        }
    }
    current_solution_id += 1
    return d


def generate_participation_for_user(user_pk, event_pks):
    regs = []
    problems = []
    for event in event_pks:
        school = random.choice(schools)
        grade = random.randint(8, 12)
        r, r_pk = generate_event_reg(user_pk, school, grade, event)
        regs.append(r)
        for prob in range(event*12, (event+1)*12):
            points = random.randint(-9, 15)
            if points <= 9:
                if points >= 0:
                    problems.append(generate_solution(r_pk, prob, points))
                else:
                    problems.append(generate_solution(r_pk, prob))
    return regs, problems


def generate_users(pks, profile_pks):
    years = range(2020, 2030)
    events = range(6)  # allowed events
    users = []
    profiles = []
    user_regs = []
    solutions = []
    for pk, prof_pk in zip(pks, profile_pks):
        users.append(generate_user(pk))
        year = random.choice(years)
        school = random.choice(schools)
        event_pks = random.sample(events, k=4)
        profiles.append(generate_profile(prof_pk, pk, year, school))
        regs, sols = generate_participation_for_user(pk, event_pks)
        user_regs += regs
        solutions += sols
    return users, profiles, user_regs, solutions


if __name__ == "__main__":

    user_pks = range(48, 78)
    users, profiles, user_regs, solutions = generate_users(user_pks, user_pks)
    with open('users_generic.json', 'w') as f:
        json.dump(users, f, indent=4)
    with open('profiles_generic.json', 'w') as f:
        json.dump(profiles, f, indent=4)
    with open('regs_generic.json', 'w') as f:
        json.dump(user_regs, f, indent=4)
    with open('solutions_generic.json', 'w') as f:
        json.dump(solutions, f, indent=4)
