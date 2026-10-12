"""Deterministically author the Air II canopy's continuous surface patches.

Run with ``uv run python scripts/refine_canopy.py``. The only component written is
specs/components/canopy.json. The frozen architecture supplies every mounting,
clamp, camera and arch anchor. Explicit mesh data, never code, enters the renderer.
"""
from __future__ import annotations

import copy
import math
from collections import Counter

import jsonschema

from contracts import ROOT, read_json, resolve, write_json

A = read_json(ROOT / 'specs/spatial_architecture.json')
P = {k: v['value'] for k, v in A['parameters'].items()}
ANG = math.radians(P['camera_tilt_deg'])
C, S = math.cos(ANG), math.sin(ANG)
COLLAR = (0., P['canopy_collar_center_y'], P['canopy_collar_center_z'])
THICK = P['canopy_strap_thickness']


def add(a, b): return tuple(x+y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def mul(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def unit(a): return mul(a, 1/max(math.sqrt(dot(a,a)), 1e-12))
def lerp(a, b, t): return add(mul(a, 1-t), mul(b, t))
def ease(t):
    t=max(0., min(1., t)); return t*t*(3-2*t)


def ref(k, scale=1., offset=0.):
    d={'param':k}
    if abs(scale-1)>1e-12: d['scale']=round(scale, 12)
    if abs(offset)>1e-12: d['offset']=round(offset, 10)
    return d


def world_ref(v):
    x,y,z=v
    return [ref('frame_mount_cardinal_offset', x/P['frame_mount_cardinal_offset']) if abs(x)>1e-12 else 0,
            ref('frame_mount_cardinal_offset', y/P['frame_mount_cardinal_offset']) if abs(y)>1e-12 else 0,
            ref('canopy_arch_peak_z', 1, z-P['canopy_arch_peak_z']) if z>38.5 else ref('canopy_mount_z',1,z-P['canopy_mount_z'])]


def to_camera(q):
    x,y,z=sub(q,COLLAR)
    # Camera-local surface coordinates: X right, U image up, A optical forward.
    return (x, -y*S+z*C, y*C+z*S)


def from_camera(q):
    x,u,a=q
    return add(COLLAR,(x,a*C-u*S,a*S+u*C))


def curve(points, steps=10):
    out=[]
    for i in range(len(points)-1):
        a,b,c,d=points[max(0,i-1)],points[i],points[i+1],points[min(len(points)-1,i+2)]
        for j in range(steps):
            t=j/steps
            q=[.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in range(3)]
            q[2]=min(P['canopy_arch_peak_z'],max(P['canopy_mount_z'],q[2]))
            out.append(tuple(q))
    out.append(tuple(points[-1]));return out


class PathCurve:
    def __init__(self, points):
        self.points=curve(points)
        self.lengths=[0.]
        for a,b in zip(self.points,self.points[1:]): self.lengths.append(self.lengths[-1]+math.dist(a,b))
        self.length=self.lengths[-1]
    def at(self,f):
        s=max(0,min(1,f))*self.length
        i=next((i for i in range(len(self.lengths)-1) if self.lengths[i+1]>=s),len(self.lengths)-2)
        t=(s-self.lengths[i])/(self.lengths[i+1]-self.lengths[i])
        return lerp(self.points[i],self.points[i+1],t)
    def frame(self,f,axis):
        q=self.at(f);tan=unit(sub(self.at(min(1,f+.001)),self.at(max(0,f-.001))))
        w=unit(sub(axis,mul(tan,dot(axis,tan))))
        n=unit(cross(tan,w))
        if n[2]<0:n=mul(n,-1)
        return q,w,n,tan


class Surface:
    def __init__(self): self.v=[];self.n=[];self.faces=[];self.tags=[];self.lookup={};self.open_groups=[]
    def vertex(self,v,n,tag=None):
        key=tuple(round(x,9) for x in v)
        if key not in self.lookup:
            self.lookup[key]=len(self.v);self.v.append(tuple(v));self.n.append(unit(n));self.tags.append(tag)
        return self.lookup[key]
    def face(self,f):
        f=list(dict.fromkeys(f))
        if len(f)>2:
            # Maintain a known outward mid-surface winding before thickening.
            fn=cross(sub(self.v[f[1]],self.v[f[0]]),sub(self.v[f[2]],self.v[f[0]]))
            expected=tuple(sum(self.n[i][k] for i in f) for k in range(3))
            if dot(fn,expected)<0:f.reverse()
            self.faces.append(f)
    def solid(self, thickness=THICK, bind=world_ref):
        used=sorted({i for face in self.faces for i in face})
        if len(used)!=len(self.v):
            remap={old:new for new,old in enumerate(used)}
            self.v=[self.v[i] for i in used];self.n=[self.n[i] for i in used];self.tags=[self.tags[i] for i in used]
            self.faces=[[remap[i] for i in face] for face in self.faces]
            self.open_groups=[{remap[i] for i in group if i in remap} for group in self.open_groups]
        count=len(self.v);vv=[]
        for sign in [-1,1]:
            for v,n,tag in zip(self.v,self.n,self.tags):
                q=add(v,mul(n,sign*thickness*.5));r=bind(q)
                if tag=='oval_inner':r[0]=ref('canopy_antenna_aperture_width',q[0]/P['canopy_antenna_aperture_width'])
                vv.append(r)
        ff=[]
        for f in self.faces:ff.extend([list(reversed(f)),[i+count for i in f]])
        counts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in self.faces for i in range(len(f)))
        for f in self.faces:
            for i,a in enumerate(f):
                b=f[(i+1)%len(f)]
                if counts[tuple(sorted((a,b)))]==1 and not any(a in group and b in group for group in self.open_groups):ff.append([a,b,b+count,a+count])
        return {'vertices':vv,'faces':ff}


def mesh_node(name, surface, note, location=None):
    if location is None:
        args=surface.solid()
    else:
        numeric=resolve(location,A['parameters'])
        args=surface.solid(bind=lambda q:[round(x,10) for x in sub(q,numeric)])
    d={'id':name,'op':'mesh','material':'canopy_white','args':args,'smooth':True,'notes':note}
    if location is not None:d['transform']={'location':location}
    return d


def crown(q,w,n,width,t,amount=.055):
    return add(add(q,mul(w,width*t)),mul(n,amount*(1-t*t)))


def strip(path,axis,width_fn,holes=(),start=0.,end=1.,segments=90):
    surface=Surface();rows=sorted(set([start+(end-start)*i/segments for i in range(segments+1)]+
        [f for h in holes for f in (h[0],h[1],(h[0]+h[1])/2) if start<=f<=end]))
    previous=None;sections={}
    for f in rows:
        q,w,n,tan=path.frame(f,axis);width=width_fn(f);hole=0.;tag=None
        for a,b,wa,wb,power,label in holes:
            if a<f<b:
                t=(f-a)/(b-a);h=(wa*(1-t)+wb*t)*(max(0,1-abs(2*t-1)**power)**(1/power))
                if h>hole:hole=h;tag=label
        # Three bands on each side; rounded edge section is established explicitly.
        xs=[-width,-width+(width-hole)/3,-width+2*(width-hole)/3,-hole,hole,hole+(width-hole)/3,hole+2*(width-hole)/3,width]
        xs=sorted(xs);ids=[]
        for x in xs:
            t=x/width
            zc=.055*(1-t*t)
            co=add(add(q,mul(w,x)),mul(n,zc))
            label=tag if hole>0 and abs(abs(x)-hole)<1e-9 else None
            ids.append(surface.vertex(co,n,label))
        if previous:
            for j in [0,1,2,4,5,6]:surface.face([previous[j],previous[j+1],ids[j+1],ids[j]])
        previous=ids;sections[round(f,10)]=(q,w,n,tan,width)
        if f==rows[0] or f==rows[-1]:surface.open_groups.append(set(ids))
    return surface,sections


def foot(name,center,section,bore=.75,radius=2.20):
    q,w,n,tan,width=section
    forward=unit((q[0]-center[0],q[1]-center[1],0))
    side=(-forward[1],forward[0],0)
    # Outer neck edge exactly matches the eight-point starting strip section.
    start_x=[-width,-width*2/3,-width/3,0.,0.,width/3,width*2/3,width]
    line=[crown(q,w,n,width,x/width) for x in start_x]
    # Determine which end proceeds around the far edge in counterclockwise order.
    if dot(w,side)<0:line=list(reversed(line))
    outline=list(line)
    a0=math.atan2(dot(sub(line[-1],center),side),dot(sub(line[-1],center),forward))
    a1=2*math.pi+math.atan2(dot(sub(line[0],center),side),dot(sub(line[0],center),forward))
    # Smooth cubic contour from neck to round pad; the fastening bore stays circular.
    for j in range(1,49):
        theta=a0+(a1-a0)*j/49
        v=add(mul(forward,math.cos(theta)*radius),mul(side,math.sin(theta)*radius))
        raw=add(center,v)
        # Blend a short region beside the neck; the far pad outline remains circular.
        edge=j/49
        if edge<.18:
            t=ease(edge/.18);raw=lerp(line[-1],raw,t)
        elif edge>.82:
            t=ease((1-edge)/.18);raw=lerp(line[0],raw,t)
        outline.append(raw)
    surface=Surface();rows=[]
    for r in [0.,.34,.70,1.]:
        ids=[]
        for k,o in enumerate(outline):
            rel=sub(o,center);theta=math.atan2(dot(rel,side),dot(rel,forward))
            inner=add(center,add(mul(forward,bore*math.cos(theta)),mul(side,bore*math.sin(theta))))
            # Neck samples use the incoming strip plane for positional/tangent continuity.
            no=n if k<len(line) else (0,0,1)
            v=lerp(inner,o,r)
            if r>.65:
                delta=sub(inner,o);proj=sub(delta,mul(no,dot(delta,no)))
                v=lerp(v,add(o,mul(proj,1-r)),ease((r-.65)/.35))
            ids.append(surface.vertex(v,lerp((0,0,1),no,r)))
        rows.append(ids)
    for a,b in zip(rows,rows[1:]):
        for j in range(len(outline)):surface.face([a[j],a[(j+1)%len(outline)],b[(j+1)%len(outline)],b[j]])
    loc=[ref('frame_mount_cardinal_offset',center[0]/P['frame_mount_cardinal_offset']) if center[0] else 0,
         ref('frame_mount_cardinal_offset',center[1]/P['frame_mount_cardinal_offset']) if center[1] else 0,ref('canopy_mount_z')]
    surface.open_groups.append(set(rows[-1][:len(line)]))
    return mesh_node('foot_'+name,surface,'Circular mounting bore and frozen screw center retained. Rounded pad transitions to a neck with exactly matching strip boundary samples; no washer/strip overlap is used.',loc)


def apply_common_normals(nodes):
    """Orient the joined shell, then share its actual geometric normal field.

    Editable patches retain their names and vertices. Coincidence is only used
    to identify true interfaces, never to displace points or cover a gap.
    """
    resolved=resolve(nodes,A['parameters']);meshes=[];owners={};edges={};records=[]
    def rotated(v,angles,inverse=False):
        q=list(v)
        for axis in ([2,1,0] if inverse else [0,1,2]):
            r=math.radians(angles[axis])*(-1 if inverse else 1);c,s=math.cos(r),math.sin(r)
            i,j=((1,2),(2,0),(0,1))[axis];q[i],q[j]=q[i]*c-q[j]*s,q[i]*s+q[j]*c
        return tuple(q)
    for original,node in zip(nodes,resolved):
        if node['op']!='mesh':continue
        tr=node.get('transform',{});loc=tr.get('location',(0,0,0));rot=tr.get('rotation_deg',(0,0,0))
        vv=[add(rotated(v,rot),loc) for v in node['args']['vertices']]
        keys=[tuple(round(c,7) for c in v) for v in vv]
        for key in keys:owners.setdefault(key,set()).add(node['id'])
        meshes.append((original,vv,keys,rot))
        for fi,face in enumerate(original['args']['faces']):
            index=len(records);records.append((original,fi,vv,keys))
            for j,i in enumerate(face):
                a,b=keys[i],keys[face[(j+1)%len(face)]]
                assert a!=b,(node['id'],'collapsed edge')
                edges.setdefault(tuple(sorted((a,b))),[]).append((index,a,b))
    assert all(len(value)==2 for value in edges.values()),Counter(len(v) for v in edges.values())
    adjacency={i:[] for i in range(len(records))}
    for pair in edges.values():
        (a,a0,a1),(b,b0,b1)=pair;same=a0==b0
        adjacency[a].append((b,same));adjacency[b].append((a,same))
    flips={};islands=[]
    for first in range(len(records)):
        if first in flips:continue
        flips[first]=False;stack=[first];island=[]
        while stack:
            current=stack.pop();island.append(current)
            for neighbour,same in adjacency[current]:
                wanted=flips[current]^same
                if neighbour in flips:assert flips[neighbour]==wanted,'Non-orientable surface'
                else:flips[neighbour]=wanted;stack.append(neighbour)
        islands.append(island)
    volumes=[]
    for island in islands:
        volume=0.
        for index in island:
            node,fi,vv,keys=records[index];face=node['args']['faces'][fi]
            if flips[index]:face=list(reversed(face))
            for a,b in zip(face[1:],face[2:]):volume+=dot(vv[face[0]],cross(vv[a],vv[b]))/6
        assert abs(volume)>1e-6,'Zero-volume joined shell'
        if volume<0:
            for index in island:flips[index]=not flips[index]
        volumes.append(abs(volume))
    for index,(node,fi,vv,keys) in enumerate(records):
        if flips[index]:node['args']['faces'][fi].reverse()
    sums={}
    for node,vv,keys,rot in meshes:
        for face in node['args']['faces']:
            origin=vv[face[0]];area=(0,0,0)
            for a,b in zip(face[1:],face[2:]):area=add(area,cross(sub(vv[a],origin),sub(vv[b],origin)))
            assert dot(area,area)>1e-18,(node['id'],'degenerate face',face)
            normal=unit(area)
            for j,i in enumerate(face):
                before=unit(sub(vv[face[j-1]],vv[i]));after=unit(sub(vv[face[(j+1)%len(face)]],vv[i]))
                angle=math.acos(max(-1,min(1,dot(before,after))))
                key=keys[i];sums[key]=add(sums.get(key,(0,0,0)),mul(normal,angle))
    for node,vv,keys,rot in meshes:
        node['args']['vertex_normals']=[[round(c,12) for c in unit(rotated(unit(sums[key]),rot,True))] for key in keys]
    interfaces=Counter(tuple(sorted(value)) for value in owners.values() if len(value)>1)
    return {'weld_tolerance_mm':1e-7,'joined_surface_closed':True,'joined_edge_count':len(edges),
            'joined_connected_shells':len(islands),'signed_outward_volumes_mm3':volumes,
            'shared_vertex_groups':[{'nodes':list(pair),'coincident_vertices':count} for pair,count in sorted(interfaces.items())],
            'normal_convention':'Globally coherent outward faces, normalized local-space vertex normals angle-weighted across true coincident interfaces; no geometric gap repair.'}


def main():
    existing=read_json(ROOT/'specs/components/canopy.json')
    hardware=[copy.deepcopy(n) for n in existing['nodes'] if n['id'] in {'clamp_tab_neg1','clamp_tab_1','clamp_cross_screw','clamp_cross_screw_head','clamp_head_slot'}]
    nodes=[];joins={};surfaces={};paths=A['anchors']['canopy_paths']
    for side in ['left','right']:
        path=PathCurve(paths[side+'_leg']);start=2.15/path.length
        def width(f):return .83+.36*math.exp(-((f-start)/.18)**2)+.69*ease((f-.72)/.28)
        surface,sections=strip(path,(0,1,0),width,start=start,segments=80)
        nodes.append(mesh_node(side+'_leg',surface,'Crowned thin leg follows frozen long centerline. Both ends terminate at shared surface boundaries: foot neck and collar shoulder. This node is now an explicit mesh, not a ribbon.'))
        start_section=sections[round(start,10)];joins[side]=sections[1.0]
        center=tuple(paths[side+'_leg'][0]);nodes.append(foot(side,center,start_section))
        surfaces[side]=surface
    front=PathCurve(paths['front_tongue']);fst=2.0/front.length
    fw=lambda f:1.34+.27*f
    front_surface,sections=strip(front,(1,0,0),fw,[(fst+.035,.90,.43,.40,4,'slot')],start=fst,segments=72)
    nodes.append(mesh_node('formed_front_tongue_with_slot',front_surface,'Continuous crowned tongue with genuine longitudinal slot and shared foot/collar boundary.'))
    nodes.append(foot('front',tuple(paths['front_tongue'][0]),sections[round(fst,10)],radius=1.98));joins['front']=sections[1.0]
    rear=PathCurve(paths['rear_arch_center']);rst=2.2/rear.length;ren=.945
    def rw(f):
        knots=[(0,1.55),(.28,1.65),(.49,2.00),(.58,3.22),(.73,3.53),(1,4.65)]
        for (a,x),(b,y) in zip(knots,knots[1:]):
            if f<=b:return x+(y-x)*ease((f-a)/(b-a))
        return knots[-1][1]
    holes=[(.085,.120,.68,.68,2,'small'),(.172,.208,.68,.68,2,'small'),(.253,.290,.68,.68,2,'small'),
           (.330,.490,1.05,1.14,3.7,'slot'),(.535,.682,P['canopy_antenna_aperture_width']/2,P['canopy_antenna_aperture_width']/2,2,'oval_inner'),
           (.731,.915,2.40,3.26,3.7,'window')]
    rear_surface,sections=strip(rear,(1,0,0),rw,holes,start=rst,end=ren,segments=110)
    nodes.append(mesh_node('formed_rear_arch_with_rounded_apertures',rear_surface,'Crowned arch preserves peak and installed path. Genuine adjustment, slot, 4.9 mm oval and trapezoidal openings retained. Its final root is absorbed into the common collar surface; the original terminal remains the unchanged construction-path anchor.'))
    nodes.append(foot('rear',tuple(paths['rear_arch_center'][0]),sections[round(rst,10)]));joins['rear']=sections[round(ren,10)]

    # Ring-shaped collar surface with three attached stem interfaces and an upper
    # arch interface. End rows are shared, not overlapping widened ribbon caps.
    spans={'right':(318,342),'rear':(48,132),'left':(198,222),'front':(252,288)}
    angles=set(range(0,360,3))
    for lo,hi in spans.values():angles.update(lo+(hi-lo)*t for t in [0,1/6,1/3,.5,2/3,5/6,1])
    angles=sorted(angles);surface=Surface();outer=[];norms=[];width_t=[]
    ordered=sorted((lo,hi,key) for key,(lo,hi) in spans.items())
    def edge_point(key,t):
        q,w,n,tan,width=joins[key]
        coeff=(1-2*t) if key in {'right','rear'} else (2*t-1)
        return crown(q,w,n,width,coeff),n
    def bridge_outer(deg):
        value=deg
        if value<ordered[0][0]:value+=360
        extended=ordered+[(ordered[0][0]+360,ordered[0][1]+360,ordered[0][2])]
        for (_,hi,key),(lo2,_,key2) in zip(extended,extended[1:]):
            if hi<value<lo2:
                t=(value-hi)/(lo2-hi);a,na=edge_point(key,1);b,nb=edge_point(key2,0)
                da=unit(sub(a,edge_point(key,.98)[0]));db=unit(sub(edge_point(key2,.02)[0],b))
                h=min(2.4,math.dist(a,b)*.27);c1=add(a,mul(da,h));c2=sub(b,mul(db,h))
                co=add(add(mul(a,(1-t)**3),mul(c1,3*(1-t)**2*t)),add(mul(c2,3*(1-t)*t*t),mul(b,t**3)))
                return co,unit(lerp(na,nb,ease(t)))
        raise ValueError(('No outer bridge',deg))
    ri=P['canopy_clamp_inner_radius']+.27
    for deg in angles:
        theta=math.radians(deg);key=next((k for k,(lo,hi) in spans.items() if lo<=deg<=hi),None)
        if key:
            lo,hi=spans[key];t=(deg-lo)/(hi-lo)
            q,w,n,tan,width=joins[key]
            # Winding follows increasing polar angle around the camera aperture.
            coeff=(1-2*t) if key in {'right','rear'} else (2*t-1)
            out=crown(q,w,n,width,coeff)
        else:
            out,n=bridge_outer(deg)
        outer.append(out);norms.append(n);width_t.append(key)
    rings=[0.,.09,.20,.35,.52,.67,.80,.91,1.]
    ids=[]
    for j,(deg,out,no) in enumerate(zip(angles,outer,norms)):
        theta=math.radians(deg);inside=from_camera((ri*math.cos(theta),ri*math.sin(theta),0))
        qo=to_camera(out);cap=max(0,math.sin(theta))**1.75
        row=[]
        for k,t in enumerate(rings):
            v=lerp(inside,out,t)
            # Fold the upper face into a thin protective lip, tapering fully at
            # both side roots instead of a separate cut-ended semicircular band.
            bump=3.00*math.exp(-((t-.25)/.20)**2)*cap
            bump*=math.sin(math.pi*t)**.55
            v=add(v,(0,C*bump,S*bump))
            # Match the strip plane in the last radial interval (C1 boundary).
            if t>.72:
                d=sub(inside,out);d=sub(d,mul(no,dot(d,no)))
                target=add(out,mul(d,1-t))
                v=lerp(v,target,ease((t-.72)/.28))
            if t==1 and width_t[j]:
                key=width_t[j];lo,hi=spans[key]
                # Collapse the dense circular sampling onto the exact seven
                # strip edge samples. Adjacent quads become valid triangles;
                # there are no T junctions or unmatched extra boundary points.
                fraction=round((deg-lo)/(hi-lo)*6)/6
                v=edge_point(key,fraction)[0]
            normal=unit(lerp((0,C,S),no,ease(t)))
            row.append(surface.vertex(v,normal))
        ids.append(row)
    for j,deg in enumerate(angles):
        nxt=(j+1)%len(angles);mid=(deg+(angles[nxt] if nxt else 360))/2
        for k in range(len(rings)-1):
            # A small genuine vent in the upper web, behind the curved cap.
            if 73<mid<107 and k in {4,5}:continue
            surface.face([ids[j][k],ids[nxt][k],ids[nxt][k+1],ids[j][k+1]])
    for key,(lo,hi) in spans.items():
        surface.open_groups.append({ids[j][-1] for j,deg in enumerate(angles) if lo<=deg<=hi})
    surface.open_groups.append({row[0] for row in ids})
    body=mesh_node('formed_collar_shoulders_with_vent',surface,'Common collar, tapered cap, cheeks and branch-root surface. Exact boundary samples coincide with crown sections of both legs, the tongue and arch. No separate brow or visible overlapping halo; a real upper vent remains.')
    nodes.append(body)
    # Explicit annular land shares the body's inner boundary tessellation. Its
    # local cylinder coordinates preserve the verified bore and camera pose.
    land=Surface();land_ids=[]
    for deg in angles:
        t=math.radians(deg);land_ids.append([land.vertex(from_camera((r*math.cos(t),r*math.sin(t),0)),(0,C,S)) for r in [P['canopy_clamp_inner_radius'],ri]])
    for j in range(len(angles)):
        nxt=(j+1)%len(angles);land.face([land_ids[j][0],land_ids[nxt][0],land_ids[nxt][1],land_ids[j][1]])
    land.open_groups.append({row[1] for row in land_ids})
    land_args=land.solid(bind=lambda q:list(to_camera(q)))
    # to_camera gives X,U,A; Blender's -65deg optical frame uses X,-U,A.
    for v in land_args['vertices']:
        r=math.hypot(v[0],v[1]);outer_offset=r-P['canopy_clamp_inner_radius'];x,y=v[0]/r,-v[1]/r
        v[:]=[ref('canopy_clamp_inner_radius',x,outer_offset*x),ref('canopy_clamp_inner_radius',y,outer_offset*y),ref('canopy_strap_thickness',v[2]/THICK)]
    nodes.append({'id':'lens_clamp_annulus','op':'mesh','material':'canopy_white','args':land_args,'transform':{'location':[0,ref('canopy_collar_center_y'),ref('canopy_collar_center_z')],'rotation_deg':[ref('camera_tilt_deg',1,-90),0,0]},'smooth':True,'notes':'Exact 10.2 mm cylindrical inner clamping land, expressed as a mesh to share boundary samples and normals with the continuous formed body. Radius, thickness and pose retain central parameter references.'})
    nodes.extend(hardware)
    junctions=apply_common_normals(nodes)
    result={'schema_version':'1.0','id':'canopy','contract':A['contract'],'description':'Air II continuous moulded canopy surface patches with a folded protective cap, real vent, crowned open straps and blended mounting-pad necks.','provenance':[
      {'feature':'nominal bores and opening','status':'verified','source_ids':['canopy_drawing','canopyii'],'confidence':'high','note':'10.2 mm lens clamping land, 1.5 mm front mounting bore, 1.1 mm clamp screw bore and 4.9 mm oval opening retain registry references. Other foot bore diameters remain a symmetry estimate.'},
      {'feature':'mounting and installed pose','status':'derived','source_ids':['frame_drawing','air_ii_canopy_side'],'confidence':'medium','note':'All four foot transform origins remain on the assembled frame screw axes. Camera/clamp and arch construction anchors are unchanged. The original rear-arch terminal remains in the frozen construction path; the moulded root is blended into the collar without forcing an artificial crease through that skin.'},
      {'feature':'moulded cap and shared roots','status':'estimated','source_ids':['air_ii_canopy_structure','air_ii_canopy_black','photo_racing_oblique','photo_freestyle_side_oblique'],'confidence':'medium','note':'Visible collar/cap/cheek surfaces form one patch network. Strip and foot/collar interfaces share boundary samples. Unmeasured taper, shallow crown, opening contour and reinforcement shapes are image-derived estimates; no older Air65 geometry is imported.'},
      {'feature':'local opening and section refinement','status':'estimated','source_ids':['air_ii_canopy_diagram','air_ii_canopy_black'],'confidence':'medium','note':'Opening order is preserved; the upper trapezoidal window ends slightly earlier to provide a continuous collar-root web. Strap thickness stays 0.65 mm, with 0.055 mm estimated mid-surface crown. Total assembled surface height includes half wall thickness.'}], 'nodes':nodes}
    jsonschema.Draft202012Validator(read_json(ROOT/'specs/component.schema.json')).validate(result)
    resolved=resolve(result,A['parameters']);assert len({n['id'] for n in nodes})==len(nodes)
    checks=[]
    for n in resolved['nodes']:
        if n['op']!='mesh':continue
        vv=n['args']['vertices'];ff=n['args']['faces'];edges=Counter()
        normals=n['args']['vertex_normals']
        assert len(normals)==len(vv) and all(abs(math.sqrt(dot(q,q))-1)<1e-9 for q in normals),n['id']
        for f in ff:
            assert len(set(f))==len(f) and 0<=min(f) and max(f)<len(vv),n['id']
            for i in range(len(f)):edges[tuple(sorted((f[i],f[(i+1)%len(f)])))]+=1
        assert all(c in {1,2} for c in edges.values()),n['id']
        checks.append({'node':n['id'],'vertices':len(vv),'faces':len(ff),'edges_with_more_than_two_faces':0,'intentional_interface_edges':sum(c==1 for c in edges.values())})
    write_json(ROOT/'specs/components/canopy.json',result)
    output=ROOT/'output/canopy_refinement';output.mkdir(parents=True,exist_ok=True)
    write_json(output/'authoring_validation.json',{'contract':A['contract'],'nodes':len(nodes),'mesh_checks':checks,'shared_boundaries':junctions,'leg_operation':'mesh','regression_change':'left/right_leg no longer have args.points; test parameter invariance on mesh args and foot transform origins.','anchor_values':{k:P[k] for k in ['frame_mount_cardinal_offset','canopy_mount_z','canopy_arch_peak_z','canopy_arch_peak_y','canopy_clamp_inner_diameter','canopy_antenna_aperture_width']}})
    print(f'Authored {len(nodes)} canopy nodes; schema, parameter, ID and surface-edge checks passed.')


if __name__=='__main__':main()
