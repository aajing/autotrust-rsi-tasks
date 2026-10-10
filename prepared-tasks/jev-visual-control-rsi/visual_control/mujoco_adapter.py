"""Optional scene exporter/render adapter, NOT authoritative scoring physics.

Requires separately installed MuJoCo and a functioning renderer. Its image
appearance is not interchangeable with the frozen CPU lane without revalidation.
"""
from xml.sax.saxutils import escape


def to_xml(env):
    geometry=[]
    for o in env.objects.values():
        color=o["color"].lstrip("#");rgb=" ".join(str(int(color[i:i+2],16)/255) for i in (0,2,4))
        size=f"{o['half']} {o['half']}" if o["shape"]=="cylinder" else " ".join([str(o["half"])]*3)
        geometry.append(f'<geom name="{escape(o["id"])}" type="{o["shape"]}" pos="{" ".join(map(str,o["position"]))}" size="{size}" rgba="{rgb} 1"/>')
    for t in env.trays.values():
        x,y=t["position"];h=t["half"]
        geometry.append(f'<geom type="box" pos="{x} {y} .003" size="{h} {h} .003" rgba=".8 .7 .25 1"/>')
    for b in env.record["obstacles"]:
        center=[(a+c)/2 for a,c in zip(b["min"],b["max"])];half=[(c-a)/2 for a,c in zip(b["min"],b["max"])]
        geometry.append(f'<geom type="box" pos="{" ".join(map(str,center))}" size="{" ".join(map(str,half))}" rgba=".3 .3 .35 1"/>')
    x,y,z=env.gripper
    geometry.append(f'<geom type="sphere" pos="{x} {y} {z}" size=".012" rgba=".1 .1 .1 1"/>')
    return '<mujoco><option timestep=".002"/><visual><global offwidth="384" offheight="384"/></visual><worldbody><light pos="0 0 2"/><geom type="plane" size=".45 .4 .01" rgba=".7 .68 .6 1"/>'+''.join(geometry)+'<camera name="top" pos="0 0 1.2" xyaxes="1 0 0 0 1 0"/><camera name="oblique" pos="0 -.8 .7" xyaxes="1 0 0 0 .7 .8"/></worldbody></mujoco>'


def render(env,camera="top"):
    import mujoco
    from PIL import Image
    model=mujoco.MjModel.from_xml_string(to_xml(env));data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    with mujoco.Renderer(model,height=384,width=384) as renderer:
        renderer.update_scene(data,camera=camera)
        return Image.fromarray(renderer.render())
