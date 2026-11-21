"""Dependency-free administrator policy shared by runtime and backup tooling."""
import json


def is_custom_user(user):
    return isinstance(user.get('categories'), list) and isinstance(user.get('permissions'), list)


def may_manage_users(user):
    return ('manage-users' in user['permissions']) if is_custom_user(user) else user.get('role') == 1


def has_active_manager(db):
    columns = {r[1] for r in db.execute('PRAGMA table_info(users)')}
    custom = {'categories', 'permissions'} <= columns
    cursor = db.execute('SELECT role,enabled' + (',categories,permissions' if custom else '') + ' FROM users')
    for row in cursor:
        if row[1] != 1:
            continue
        user = {'role': row[0]}
        if custom and (row[2] is not None or row[3] is not None):
            try:
                categories, permissions = json.loads(row[2]), json.loads(row[3])
                if not all(isinstance(x, list) and all(isinstance(v, str) for v in x) for x in (categories, permissions)):
                    continue
                user.update(categories=categories, permissions=permissions)
            except (ValueError, TypeError):
                continue
        if may_manage_users(user):
            return True
    return False
