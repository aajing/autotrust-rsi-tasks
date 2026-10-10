"""Public full-state reference controller. Inspection is allowed; per-scene
solution replay is not an eligible candidate controller."""
from .environment import Environment


def reference_actions(record):
    env=Environment(record); actions=[]
    def send(dx=0,dy=0,dz=0,grip=None):
        action={"dx":round(dx,9),"dy":round(dy,9),"dz":round(dz,9),"grip":env.grip if grip is None else grip}
        actions.append(action);env.step(action)
        if env.done and not env.success:
            raise ValueError("reference failed: "+env.reason)
    def move(point):
        while max(abs(a-b) for a,b in zip(point,env.gripper))>1e-7:
            delta=[max(-.04,min(.04,a-b)) for a,b in zip(point,env.gripper)]
            send(*delta)
    for goal in record["goals"]:
        obj=env.objects[goal["object"]]
        target=list(obj["position"])
        tray=env.trays[goal["tray"]]
        move([env.gripper[0],env.gripper[1],.24])
        # For this frozen geometry all initial objects are on the source side;
        # a return from a previous destination uses the same safe corridor.
        if record["obstacles"] and env.gripper[0]>0:
            move([env.gripper[0],-.20,.24]);move([target[0],-.20,.24])
        move([target[0],target[1],.24])
        move([target[0],target[1],target[2]+.045]);send(grip=0)
        move([target[0],target[1],.24])
        if record["obstacles"]:
            move([target[0],-.20,.24]);move([tray["position"][0],-.20,.24])
        move([*tray["position"],.24])
        move([*tray["position"],.085]);send(grip=1)
        while not env.done and not env.completed[record["goals"].index(goal)]:
            send()
    if not env.success:
        raise ValueError("reference did not finish")
    return actions


def certify(record):
    actions=reference_actions(record)
    env=Environment(record)
    for action in actions:env.step(action)
    if not env.success or env.steps>120:
        raise ValueError("certificate replay failed")
    return {"schema":1,"kind":"public_full_state_reference_replay_not_model_performance",
            "scene_id":record["id"],"geometry_sha256":record["geometry_sha256"],
            "actions":actions,"event":env.event(),"success":True,
            "visibility_contract":"Only one camera has a partial overlay; second view renders all objects. This is renderer-level visibility, not learned recognition."}
