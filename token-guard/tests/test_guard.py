import tempfile, unittest
from pathlib import Path
from token_guard.config import GuardConfig
from token_guard.guard import TokenGuard, ViolationBlocked
from token_guard.models import RequestRecord

class GuardTests(unittest.TestCase):
    def record(self, guard): return guard.record(RequestRecord(provider="test",model="unit",input_tokens=10,output_tokens=2,task_id="job"), content="repeat me")
    def test_strict_repeats_trigger_on_fourth_call(self):
        with tempfile.TemporaryDirectory() as d:
            g=TokenGuard(Path(d)/"db.sqlite3", GuardConfig(strictness=10))
            for _ in range(3): self.assertFalse(self.record(g))
            issues=self.record(g)
            self.assertEqual(issues[0].rule,"duplicate_request")
            self.assertEqual(g.storage.summary()["violations"],1)
            g.close()
    def test_block_action_raises_after_recording(self):
        with tempfile.TemporaryDirectory() as d:
            g=TokenGuard(Path(d)/"db.sqlite3", GuardConfig(strictness=10,action="block"))
            for _ in range(3): self.record(g)
            with self.assertRaises(ViolationBlocked): self.record(g)
            self.assertEqual(g.storage.summary()["requests"],4)
            g.close()
    def test_limits_detected(self):
        with tempfile.TemporaryDirectory() as d:
            g=TokenGuard(Path(d)/"db.sqlite3", GuardConfig(max_context_tokens=10,max_output_tokens=5))
            issues=g.record(RequestRecord(provider="x",model="m",input_tokens=11,output_tokens=6))
            self.assertEqual({x.rule for x in issues},{"oversized_context","excessive_output"})
            g.close()
if __name__ == "__main__": unittest.main()
