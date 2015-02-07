from router import Router, default_relays


r = Router(default_relays(), 100)

print Router.optimal_relay_list

phones = range(30)

print [r.throughput for r in r.optimal(len(phones))]