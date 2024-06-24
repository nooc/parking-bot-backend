import httpx

types = [
    "PublicTimeParkings",
    "PublicTollParkings",
    "PrivateTollParkings",
    "ParkingOwners",
]
domen = 
tpl = "https://data.goteborg.se/ParkingService/v2.2/{TYPE}/d6dd790a-bd47-45e8-93f5-610a5c35b7f0/1384?format=Json"

for t in types:
    r = httpx.get(url=tpl.replace("{TYPE}", t))
    if r.status_code >= 400:
        print(t, "gave", r.status_code)
    else:
        print(t, ":")
        print(r.text)
