"""Retain the upstream DUO130 bad/safe algorithm controls after syntax repair."""
import ast
import unittest

import dlint


class HashlibRuleTests(unittest.TestCase):
    def results(self, source):
        linter = dlint.linters.BadHashlibUseLinter()
        linter.visit(ast.parse(source))
        return list(linter.get_results())

    def test_unsafe_algorithms_still_report(self):
        results = self.results('import hashlib\nhashlib.md5()\nhashlib.sha1()')
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.message.startswith('DUO130 ') for r in results))

    def test_security_true_still_reports(self):
        results = self.results('import hashlib\nhashlib.md5(usedforsecurity=True)\nhashlib.sha1(usedforsecurity=True)')
        self.assertEqual(len(results), 2)

    def test_explicit_nonsecurity_and_safe_algorithm_stay_valid(self):
        results = self.results('import hashlib\nhashlib.md5(usedforsecurity=False)\nhashlib.sha1(usedforsecurity=False)\nhashlib.sha256()')
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
