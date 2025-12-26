from google.cloud import ndb


client = ndb.Client()
with client.context():
    query = ndb.Query(kind="Crunch")
    for entity in query.fetch():
        print(entity)
