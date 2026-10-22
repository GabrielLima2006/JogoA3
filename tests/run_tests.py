"""Roda todos os testes automatizados (sem janela).

    python tests/run_tests.py            # tudo
    python tests/run_tests.py boss dash  # só testes cujo nome contém essas palavras
"""

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import helpers  # noqa: E402
import test_mechanics  # noqa: E402
import test_menus  # noqa: E402
import test_ship  # noqa: E402
import test_world  # noqa: E402


def main():
    only = sys.argv[1:]
    t0 = time.time()
    for module in (test_mechanics, test_world, test_menus, test_ship):
        for test in module.TESTS:
            if only and not any(o in test.__name__ for o in only):
                continue
            print(test.__name__)
            try:
                test()
            except Exception:
                helpers.RESULTS.append((test.__name__, False, "exceção"))
                traceback.print_exc()
    results = helpers.RESULTS
    fails = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(fails)}/{len(results)} verificações passaram em {time.time() - t0:.1f}s")
    for name, _, detail in fails:
        print(f"  FALHA: {name} {detail}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
