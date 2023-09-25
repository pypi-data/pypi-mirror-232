import os
import sys

cur_file_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = f'{cur_file_dir}/../fabrique_nodes_core'
sys.path.append(lib_dir)
os.chdir(cur_file_dir)

import tests.import_spoofer  # noqa: F401

from fabrique_nodes_core.db.fake_db import FakeDB as DB
# from fabrique_nodes_core.db import DB


# @patch('fabrique_nodes_core.crypto.DB', new=FakeDB)
def test_blocking():
    user_id = '_user_id_'
    db = DB()
    _user_id, username, is_blocked = db.admin_get_user_is_blocked(user_id)
    assert not is_blocked
    assert username == ''
    assert _user_id == user_id

    db.admin_update_user_permissions(user_id, '')
    _user_id, username, is_blocked = db.admin_get_user_is_blocked(user_id)
    assert is_blocked
    assert username == ''
    assert _user_id == user_id

    db.admin_update_user_permissions(user_id, 'username', False)
    _user_id, username, is_blocked = db.admin_get_user_is_blocked(user_id)
    assert not is_blocked
    assert username == 'username'
    assert _user_id == user_id

    db.admin_delete_user_permissions(user_id)
    _user_id, username, is_blocked = db.admin_get_user_is_blocked(user_id)
    assert not is_blocked
    assert username == ''
    assert _user_id == user_id
