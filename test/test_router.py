import unittest
import os
import sys

#TODO do that better?
scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(scriptpath, "..", "src", "lib"))

import router

test_relays = [
        router.Relay('Small', '10.0.1.0', 1, 0.01),
        router.Relay('Medium', '10.0.2.0', 5, 0.05),
        router.Relay('Large', '10.0.3.0', 21, 0.21),
        router.Relay('Super', '10.0.4.0', 25, 0.25)
    ]

class TestRouterModule(unittest.TestCase):

    def setUp(self):
        pass

    def test_optimal_normal(self):
        r = router.Router(test_relays, 100)

        result = r.optimal(63)

        expected_result = [
            test_relays[2],
            test_relays[2],
            test_relays[2]
        ]

        #Converting as set as order doesn't matter
        self.assertEqual(set(expected_result), set(result))

        #---
        result = r.optimal(56)

        expected_result = [
            test_relays[3],
            test_relays[3],
            test_relays[1],
            test_relays[0]
        ]
        self.assertEqual(set(expected_result), set(result))

        #---
        r = router.Router(test_relays, 5000)

        result = r.optimal(12)

        expected_result = [
            test_relays[0],
            test_relays[0],
            test_relays[1],
            test_relays[1]
        ]
        self.assertEqual(set(expected_result), set(result))

        #---
        r = router.Router(test_relays, 5000)

        result = r.optimal(12)

        expected_result = [
            test_relays[0],
            test_relays[0],
            test_relays[1],
            test_relays[1]
        ]
        self.assertEqual(set(expected_result), set(result))

        #---
        result = r.optimal(1)

        expected_result = [
            test_relays[0]
        ]
        self.assertEqual(set(expected_result), set(result))

    def test_optimal_errors(self):
        with self.assertRaises(router.RouterException) as cm:
            r = router.Router([])
        self.assertEqual(("A list of relays is necessary",), cm.exception.args)

        with self.assertRaises(router.RouterException) as cm:
            r = router.Router(test_relays, 5)
            r.optimal(10)
        self.assertEqual(("The number of phones exceeded the range of pre-processed values",), cm.exception.args)

        with self.assertRaises(router.RouterException) as cm:
            r = router.Router(test_relays, -1)
            r.optimal(10)
        self.assertEqual(("The number of phones exceeded the range of pre-processed values",), cm.exception.args)

        with self.assertRaises(router.RouterException) as cm:
            r = router.Router(test_relays, 0)
            r.optimal(10)
        self.assertEqual(("The number of phones exceeded the range of pre-processed values",), cm.exception.args)

        with self.assertRaises(router.RouterException) as cm:
            r = router.Router([test_relays[0],test_relays[2]])
            r.optimal(-1)
        self.assertEqual(("Number of phones must be greater than 0.",), cm.exception.args)

        with self.assertRaises(router.RouterException) as cm:
            relays = [test_relays[3]]
            r = router.Router(relays)
        self.assertEqual(("First Relay throughput must be 1",), cm.exception.args)

    def test_greedy(self):
        with self.assertRaises(router.RouterException) as cm:
            r = router.Router(test_relays, 0)
            r.greedy()
        self.assertEqual(("Not Implemented",), cm.exception.args)

if __name__ == '__main__':
    #TODO use nosetests?
    unittest.main()