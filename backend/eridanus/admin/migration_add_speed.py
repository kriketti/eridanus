# --- migration_add_speed.py ---
# Rulează acest script în contextul aplicației tale
# (de ex. folosind 'flask shell' sau un mecanism similar)

from google.cloud import ndb
from eridanus.models import Run

def migrate_runs():
    """
    Iterează prin toate entitățile 'Run' și le re-salvează pentru a
    activa logica ComputedProperty pentru 'speed'.
    """
    print("Începe migrarea pentru entitățile Run...")
    
    all_runs = Run.query().fetch()
    
    # Pentru un număr mare de entități, este mai eficient să folosești 'put_multi' în batch-uri
    batch_size = 200
    updated_runs = []
    
    for i, run in enumerate(all_runs):
        # Nu trebuie să modifici nimic. Doar adaugi entitatea în listă.
        updated_runs.append(run)
        
        # Când batch-ul este plin sau am ajuns la final, îl salvăm
        if len(updated_runs) == batch_size or i == len(all_runs) - 1:
            print(f"Se salvează un batch de {len(updated_runs)} entități...")
            ndb.put_multi(updated_runs)
            updated_runs = [] # Golește batch-ul
            
    print("Migrarea a fost finalizată!")

# Pentru a rula migrarea:
# 1. Intră în contextul aplicației (ex: `flask shell`)
# 2. from scripts.migration_add_speed import migrate_runs
# 3. client = ndb.Client()
# 4. with client.context():
# 5.     migrate_runs()
