WAITING_CHANNEL = '$w'

SERVER_CODES = {  # 메시지 브로커 코드
    'game_data': 'gd',
    'game_over': 'go',
    'match_set': 'ms',
    'game_start': 'gs',
    'host_accepted': 'ha',
    'host_rejected': 'hr',
    'approacher_updated': 'au',
    'match_complete': 'mc',
    'loser': 'lo',
    'winner': 'wi',
    'waiter_list': 'wl'
}

USER_SCODES = {  # 유저가 전송하는 코드
    'game_data': 'gd',
    'game_over': 'go',
    'waiting_list_add': 'wa',
    'waiting_list_remove': 'wr',
    'waiting_list_get': 'wg',
    'approach': 'a',
    'approach_cancel': 'ac',
    'host_accept': 'ha',
    'host_reject': 'hr',
}

USER_RCODES = {  # 유저가 받는 코드
    'game_data': 'gd',
    'game_over': 'go',
    'match_set': 'ms',  # 현재는 사용할 필요 없음
    'match_complete': 'mc',
    'game_start': 'gs',
    'waiter_list': 'wl',
    'host_accepted': 'ha',
    'host_rejected': 'hr',
    'approacher_list': 'al',
    'lose': 'lo',
    'win': 'wi'
}

