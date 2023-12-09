def rank_results(results: list[dict]) -> list[dict]:
    # Spodná hranica
    current_rank = 1
    n_teams = 1
    last_points = None
    for res in results:
        if last_points != res['total']:
            current_rank = n_teams
            last_points = res['total']
            res['rank_changed'] = True
        else:
            res['rank_changed'] = False
        res['rank_start'] = current_rank
        n_teams += 1

    # Horná hranica
    current_rank = len(results)
    n_teams = len(results)
    last_points = None
    for res in reversed(results):
        if last_points != res['total']:
            current_rank = n_teams
            last_points = res['total']
        res['rank_end'] = current_rank
        n_teams -= 1
    return results


def generate_praticipant_invitations(
        results_with_ranking: list[dict],
        number_of_participants: int,
        number_of_substitues: int) -> list[dict]:
    invited_users = []
    for i, result_row in enumerate(results_with_ranking):
        if i < number_of_participants:
            invited_users.append({
                'first_name': result_row['registration']['profile']['first_name'],
                'last_name': result_row['registration']['profile']['last_name'],
                'school': result_row['registration']['school'],
                'is_participant': True
            })
        elif i < number_of_participants+number_of_substitues:
            invited_users.append({
                'first_name': result_row['registration']['profile']['first_name'],
                'last_name': result_row['registration']['profile']['last_name'],
                'school': result_row['registration']['school'],
                'is_participant': False
            })
    return invited_users
