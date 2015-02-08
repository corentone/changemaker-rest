import logging

logger = logging.getLogger('router')

class RouterException(Exception):
    """Base class for exceptions in this module."""
    pass

class Relay(object):
    def __init__(self, name, ip, throughput, cost):
        self.name = name
        self.ip = ip
        self.throughput = throughput
        self.cost = cost

def default_relays():
    """ Return a list of default relays

        Returns a list of Relay objects
    """

    return [
        Relay('Small', '10.0.1.0', 1, 0.01),
        Relay('Medium', '10.0.2.0', 5, 0.05),
        Relay('Large', '10.0.3.0', 10, 0.1),
        Relay('Super', '10.0.4.0', 25, 0.25)
    ]


class Router(object):
    optimal_max_phones = 0
    optimal_relay_list = []
    relays = [] # use objects

    def __init__(self, relays, size_optimal=5000):
        if not relays:
            raise RouterException("A list of relays is necessary")

        if set(relays) != Router.relays:
            Router.__deinit_optimal()

        Router.relays = relays
        Router.__init_optimal(size_optimal)

    @staticmethod
    def __init_optimal(size_optimal):
        """Initialize the optimal algorithm cache table



        """
        Router.optimal_relay_list = [0] * (size_optimal + 1)
        minRelays = [0] * (size_optimal + 1)

        if size_optimal < Router.optimal_max_phones:
            # In this case no need to recreate the values
            return

        Router.optimal_max_phones = size_optimal

        if Router.relays[0].throughput != 1: # See the comments in the loop.
            raise RouterException("First Relay throughput must be 1")

        for num_phones in range(Router.optimal_max_phones+1):
            count = num_phones
            newRelay = Router.relays[0] # This assumes the lowest relay is throughput 1.
            #newRelay = None #In the case we cannot make this particular price ?
            # Gotta change the if statement "< count" as 1 < 1 test false.
            for r in [c for c in Router.relays if c.throughput <= num_phones]:
                if minRelays[num_phones-r.throughput] + 1 < count:
                    count = minRelays[num_phones-r.throughput]+1
                    newRelay = r
            minRelays[num_phones] = count
            Router.optimal_relay_list[num_phones] = newRelay

    @staticmethod
    def __deinit_optimal():
        Router.optimal_max_phones = 0
        Router.optimal_relay_list = []

    def optimal(self, num_phones):
        """Return the optimal routing


            See http://interactivepython.org/runestone/static/pythonds/Recursion/DynamicProgramming.html
        """

        if num_phones < 1:
            raise RouterException("Number of phones must be greater than 0.")

        if Router.optimal_max_phones < num_phones:
            # We could extend the range here...but what would be a good limit?
            raise RouterException("The number of phones exceeded the range of pre-processed values")

        l = []

        while num_phones > 0:
            r = Router.optimal_relay_list[num_phones]
            l.append(r)
            num_phones -= r.throughput

        return l

    def greedy(self):
        """Return the greedy algorithm routing"""
        raise RouterException("Not Implemented")