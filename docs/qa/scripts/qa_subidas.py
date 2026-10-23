from qa_common import *
def ground_in(rid):
    return lambda s: s.play.room.id == rid and s.p.on_ground
for ab in (("dash",), ("dash", "double_jump")):
    s = game(ab, name="qa_sub.json")
    print(ab)
    print("  porão1 -> pisa no convés:", try_reach(s, "porao1", 21, 3, ground_in("conves"), max_time=3.0))
    print("  convés topo -> pisa no cordame1:", try_reach(s, "conves", 34, 4, ground_in("cordame1"), max_time=3.0))
