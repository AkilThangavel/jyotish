from opensky import OpenSkyApi

api = OpenSkyApi()
# bbox = (min latitude, max latitude, min longitude, max longitude)
states = api.get_states()
print(len(states.states))
for s in states.states[:1000]:
    print(s.longitude, s.latitude, s.velocity, s.velocity, s.on_ground)
