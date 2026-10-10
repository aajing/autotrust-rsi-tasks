"""Local-only native JEV S1 client. A diagnostic driver, not a trusted sandbox."""
import base64,io,json,math,time,urllib.request,urllib.parse
from pathlib import Path

RAW=("{%- for m in messages -%}{%- for c in m['content'] -%}{%- if c['type'] == 'text' -%}{{ c['text'] }}"
     "{%- else -%}<|vision_start|><|image_pad|><|vision_end|>{%- endif -%}{%- endfor -%}{%- endfor -%}")

class LocalJEV:
    def __init__(self,model_dir,image_dir,base_url='http://127.0.0.1:8000',max_calls=1920,seconds=5400):
        u=urllib.parse.urlparse(base_url)
        if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost','::1') or u.username:
            raise ValueError('Only a local frozen-model endpoint is allowed')
        p=Path(model_dir);self.head=json.loads((p/'adapter_vllm/decision_head.json').read_text())
        self.temp=json.loads((p/'calibration.json').read_text())['per_kind']['noul']
        if self.temp<=0 or not math.isfinite(self.temp): raise ValueError('Invalid calibration')
        self.image_dir=Path(image_dir).resolve();self.url=base_url.rstrip('/')+'/v1/chat/completions'
        self.calls=0;self.max_calls=max_calls;self.tokens=0;self.started=time.monotonic();self.seconds=seconds
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def decide(self,parts,question):
        if self.calls>=self.max_calls or time.monotonic()-self.started>=self.seconds: raise ValueError('Budget exhausted')
        content=[{'type':'text','text':'[kind] noul\n[state] '}];n_images=0
        for part in parts:
            if isinstance(part,str):content.append({'type':'text','text':part});continue
            relative=Path(part['image'])
            if relative.is_absolute() or '..' in relative.parts or relative.parts[0]!='images': raise ValueError('Invalid asset path')
            path=(self.image_dir/relative.name).resolve()
            if path.parent!=self.image_dir: raise ValueError('Asset outside image root')
            from PIL import Image
            with Image.open(path) as im:
                im=im.convert('RGB');im.thumbnail((448,448));buf=io.BytesIO();im.save(buf,format='PNG')
            content.append({'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}})
            n_images+=1
        if n_images>8: raise ValueError('Image budget exceeded')
        content.append({'type':'text','text':'\n[question] '+question+'\n[options]\nfalse\ntrue\n[decision]:'})
        slot=self.head['slots']['ranges']['noul'][0];ids=self.head['verbalizer_ids'][slot:slot+2]
        payload={'model':'jev-decision','messages':[{'role':'user','content':content}],'chat_template':RAW,
                 'add_generation_prompt':False,'add_special_tokens':False,'max_tokens':1,'temperature':1.0,
                 'logprobs':True,'top_logprobs':2,'allowed_token_ids':ids,'return_tokens_as_token_ids':True}
        self.calls+=1
        remaining=self.seconds-(time.monotonic()-self.started)
        if remaining<=0: raise ValueError('Budget exhausted')
        req=urllib.request.Request(self.url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        with self.opener.open(req,timeout=min(120,remaining)) as r: result=json.load(r)
        usage=result.get('usage',{});tokens=usage.get('prompt_tokens')
        if not isinstance(tokens,int) or tokens<0: raise ValueError('Server did not report processor-token usage')
        self.tokens+=tokens
        if tokens>8192: raise ValueError('Processor-token envelope exceeded; run invalid')
        lp={int(t['token'].split(':')[1]):t['logprob'] for t in result['choices'][0]['logprobs']['content'][0]['top_logprobs']}
        if any(t not in lp or not math.isfinite(lp[t]) for t in ids): raise ValueError('Incomplete verbalizer probabilities')
        z=[(lp[t]+self.head['bias'][slot+i])/self.temp for i,t in enumerate(ids)]
        e=[math.exp(x-max(z)) for x in z]
        return e[1]/sum(e)
