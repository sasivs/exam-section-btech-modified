from django.db import connection
from django.apps import apps

def drop_models():
    names = [x.__name__ for x in apps.get_models() if x.__name__.startswith('BT') or x.__name__.startswith('MT')]
    cursor = connection.cursor()
    parts = ['DROP TABLE IF EXISTS \"%s\" cascade;' % table for table in names]
    for part in parts:
        cursor.execute(part)
    cursor.close()

def update_index():
    names = [x.__name__ for x in apps.get_models() if not (x.__name__.endswith('MV') or x.__name__.endswith('V'))]
    cursor = connection.cursor()
    for name in names:
        print(name)
        try:
            cursor.execute('select max(id) from \"%s\";'%name)
            highest_id = int(cursor.fetchone()[0])+1
            query = 'alter sequence \"'+name+'_id_seq\"'+' restart with '+str(highest_id)
            cursor.execute(query)
        except:
            pass
    cursor.close()