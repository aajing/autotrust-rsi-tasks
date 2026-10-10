import base64
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
from PIL import Image
from visual_control.contract import FAMILIES, TIERS, score_events, validate_action
from visual_control.environment import Environment
from visual_control.authoring import reference_actions
from visual_control.model_client import ModelClient
from visual_control.mujoco_adapter import to_xml
from visual_control.runtime import Worker, claim_attempt, worker_command
from visual_control.budget import WorkBudget

ROOT=Path(__file__).resolve().parents[1]

def records(split):
    return [json.loads(x) for x in (ROOT/"data"/split/"scenes.jsonl").read_text().splitlines()]

def move(env, point, grip=1):
    while not env.done and max(abs(a-b) for a,b in zip(point,env.gripper))>1e-7:
        d=[max(-.04,min(.04,a-b)) for a,b in zip(point,env.gripper)]
        env.step(dict(zip(("dx","dy","dz","grip"),[*d,grip])))


class CPUSuite(unittest.TestCase):
    def test_all_224_certificates_and_frozen_hashes(self):
        manifest=json.loads((ROOT/"data/manifest.json").read_text())
        seen=set();seeds=set();count=0
        partitions={"train":set(range(6)),"development":{6,7},"evaluation":{8,9}}
        for rel,info in manifest["files"].items():
            self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),info["sha256"])
        for split in ("train","development","evaluation"):
            rows=records(split)
            certs=[json.loads(x) for x in (ROOT/"data"/split/"certificates.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows),128 if split=="train" else 48)
            for record,cert in zip(rows,certs):
                self.assertNotIn(record["seed"],seeds);seeds.add(record["seed"])
                self.assertNotIn(record["geometry_sha256"],seen);seen.add(record["geometry_sha256"])
                self.assertIn(int(record["geometry_sha256"][:8],16)%10,partitions[split])
                self.assertEqual(cert["scene_id"],record["id"])
                env=Environment(record)
                for action in cert["actions"]:env.step(action)
                self.assertTrue(env.success,record["id"])
                self.assertIsNone(env.held)
                self.assertTrue(all(s>=.5-1e-8 for s in env.stable))
                self.assertLessEqual(env.steps,120);count+=1
        self.assertEqual(count,224)

    def test_action_schema_nonfinite_boolean_and_bounds(self):
        for action in ({"dx":float("nan"),"dy":0,"dz":0,"grip":1},
                       {"dx":True,"dy":0,"dz":0,"grip":1},
                       {"dx":.041,"dy":0,"dz":0,"grip":1},
                       {"dx":0,"dy":0,"dz":0,"grip":1,"success":True}):
            with self.assertRaises(ValueError):validate_action(action)
            env=Environment(records("development")[0]);env.step(action)
            self.assertTrue(env.invalid);self.assertEqual(env.event()["status"],"candidate_invalid")

    def test_swept_barrier_collision(self):
        row=next(r for r in records("development") if r["family"]=="obstacle_transport")
        env=Environment(row)
        move(env,[.10,0,.24])
        self.assertTrue(env.done);self.assertFalse(env.success);self.assertEqual(env.reason,"barrier_collision")

    def test_order_must_settle_before_second_grasp(self):
        row=next(r for r in records("development") if r["family"]=="ordered_two_place")
        env=Environment(row);obj=env.objects[row["goals"][1]["object"]]
        move(env,[obj["position"][0],obj["position"][1],.24])
        move(env,[obj["position"][0],obj["position"][1],obj["position"][2]+.045])
        env.step({"dx":0,"dy":0,"dz":0,"grip":0})
        self.assertEqual(env.reason,"order_violation");self.assertFalse(env.success)

    def test_non_target_motion_is_failure(self):
        row=records("development")[0];env=Environment(row)
        targets={g["object"] for g in env.goals};obj=next(o for k,o in env.objects.items() if k not in targets)
        move(env,[obj["position"][0],obj["position"][1],.24])
        move(env,[obj["position"][0],obj["position"][1],obj["position"][2]+.045])
        env.step({"dx":0,"dy":0,"dz":0,"grip":0})
        env.step({"dx":0,"dy":0,"dz":.04,"grip":0})
        self.assertEqual(env.reason,"non_target_displacement")

    def test_precision_is_not_just_inside_tray(self):
        row=next(r for r in records("development") if r["family"]=="precision_place" and r["tier"]=="harder")
        env=Environment(row)
        for a in reference_actions(row):
            if a["grip"]==1 and env.held:
                a=dict(a,dx=.0035)
            env.step(a)
        while not env.done:env.step({"dx":0,"dy":0,"dz":0,"grip":1})
        self.assertFalse(env.success);self.assertEqual(env.reason,"step_exhaustion")

    def test_observation_schema_and_two_step_delay(self):
        row=next(r for r in records("development") if r["tier"]=="harder")
        env=Environment(row);initial=env.observation()
        expected={"goal","placements","images","image_age_steps","proprioception","previous_action","remaining_steps","calibration"}
        self.assertEqual(set(initial),expected)
        encoded=json.dumps(initial)
        for forbidden in ("geometry_sha256",'"seed"','"held"','"scene_id"','"objects"','"trays"','"target_pose"'):
            self.assertNotIn(forbidden,encoded)
        for _ in range(2):env.step({"dx":.01,"dy":0,"dz":0,"grip":1})
        delayed=env.observation()
        self.assertEqual(delayed["image_age_steps"],2)
        self.assertEqual(initial["images"],delayed["images"])
        self.assertNotEqual(initial["proprioception"],delayed["proprioception"])
        for value in delayed["images"].values():
            im=Image.open(io.BytesIO(base64.b64decode(value.split(",",1)[1])));self.assertEqual(im.size,(384,384))

    def test_score_exact_coverage_and_failure_semantics(self):
        rows=records("evaluation")
        events=[dict(id=r["id"],family=r["family"],tier=r["tier"],status="completed",success=True,steps=35) for r in rows]
        self.assertEqual(score_events(events,rows)["score"],100)
        events[0]["success"]=False;self.assertAlmostEqual(score_events(events,rows)["score"],100*47/48)
        with self.assertRaises(ValueError):score_events(events[:-1],rows)
        events[0]["status"]="candidate_invalid"
        with self.assertRaises(ValueError):score_events(events,rows)

    def test_step_exhaustion(self):
        env=Environment(records("development")[0])
        for _ in range(120):env.step({"dx":0,"dy":0,"dz":0,"grip":1})
        self.assertEqual(env.reason,"step_exhaustion");self.assertFalse(env.success)

    def test_native_client_rejects_remote_and_missing_images(self):
        with self.assertRaises(ValueError):ModelClient("https://example.org/v1/decide",time.monotonic()+1)
        client=ModelClient("http://127.0.0.1:8000/v1/decide",time.monotonic()+1)
        with self.assertRaises(ValueError):client.decide({"kind":"choice","state":[],"question":"?","options":["a","b"],"thinking":"off"})
        self.assertEqual(client.calls,0)

    def test_native_ipc_transport_and_failed_attempt_accounting(self):
        with tempfile.TemporaryDirectory() as d:
            work=Path(d)
            (work/"candidate_worker.py").write_bytes((ROOT/"visual_control/candidate_worker.py").read_bytes())
            self.assertIn("-I",worker_command(work,ROOT/"data"))
            self.assertIn("-I",worker_command(work,ROOT/"data"))
            (work/"candidate_worker.py").write_text("print('untrusted modified transport')")
            with self.assertRaisesRegex(ValueError,"owner-frozen transport"):
                worker_command(work,ROOT/"data")
            path=Path(d)/"ledger.jsonl"
            for _ in range(12):claim_attempt(path)
            with self.assertRaises(ValueError):claim_attempt(path)
            self.assertEqual(len(path.read_text().splitlines()),12)

    def test_optional_mujoco_xml_is_well_formed_only(self):
        xml=to_xml(Environment(records("development")[0]))
        self.assertEqual(ET.fromstring(xml).tag,"mujoco")

    def test_persistent_work_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            budget=WorkBudget(directory,"candidate0")
            budget.charge_call();budget.charge_new_episode()
            self.assertEqual(json.loads(budget.path.read_text())["calls"],1)
            state=json.loads(budget.path.read_text());state.update(calls=20000,new_episodes=160)
            budget.path.write_text(json.dumps(state))
            again=WorkBudget(directory,"candidate0")
            with self.assertRaises(ValueError):again.charge_call()
            with self.assertRaises(ValueError):again.charge_new_episode()

    def test_public_evaluation_distribution(self):
        seed=json.loads((ROOT/"data/authoring_seed.json").read_text())
        self.assertEqual(seed["scope"],"public_inspection_and_reproduction")
        manifest=json.loads((ROOT/"data/manifest.json").read_text())
        self.assertIn("data/evaluation/scenes.jsonl",manifest["files"])
        self.assertIn("data/evaluation/certificates.jsonl",manifest["files"])
        self.assertNotIn("data/judge/scenes.jsonl",manifest["files"])
        self.assertIn("inspection permitted",manifest["distribution"])

    def test_native_worker_ipc_with_synthetic_transport_fixture(self):
        # Protocol plumbing only: fixture probabilities are not model inference
        # and no environment action, episode or baseline score is executed.
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)
            (work/"candidate_worker.py").write_bytes((ROOT/"visual_control/candidate_worker.py").read_bytes())
            (work/"controller.py").write_bytes((ROOT/"visual_control/baseline.py").read_bytes())
            worker=Worker(worker_command(work,ROOT/"data"),str(work),time.monotonic()+10)
            try:
                worker.send({"kind":"reset"});self.assertEqual(worker.read(),{"kind":"ready"})
                worker.send({"kind":"step","observation":Environment(records("development")[0]).observation()})
                for _ in range(2):
                    request=worker.read();self.assertEqual(request["kind"],"model_request")
                    self.assertEqual(request["payload"]["thinking"],"off")
                    worker.send({"kind":"model_response","result":{"probabilities":[.4,.6]}})
                response=worker.read();self.assertEqual(response["kind"],"action")
                validate_action(response["action"])
            finally:worker.close()


if __name__=="__main__":unittest.main()
