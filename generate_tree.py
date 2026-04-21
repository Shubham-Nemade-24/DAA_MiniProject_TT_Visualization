"""
Standalone simulation of the backtracking algorithm using the exact same
logic as app/algorithms/backtracking.py with DEMO MODE enabled.
Outputs the tree JSON + assignment for the website visualizer.
"""
import json

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
LECTURE_SLOTS = [('08:00','09:00'),('09:00','10:00'),('10:00','11:00'),('11:00','12:00'),
                 ('13:00','14:00'),('14:00','15:00'),('15:00','16:00'),('16:00','17:00')]
LAB_SLOTS = [('08:00','10:00'),('10:00','12:00'),('13:00','15:00'),('15:00','17:00')]
MAX_LABS = 2
MAX_LECTS = 4

def is_overlap(s1,e1,s2,e2):
    return not (e1<=s2 or s1>=e2)

def is_valid(assignment, ne):
    lc=0; bc=0
    for e in assignment:
        if e['day']==ne['day']:
            if e['stype']=='Lab': bc+=1
            else: lc+=1
            if e['course']==ne['course']: return False
            if is_overlap(e['ts'],e['te'],ne['ts'],ne['te']):
                return False
    if ne['stype']=='Lab' and bc>=MAX_LABS: return False
    if ne['stype']!='Lab' and lc>=MAX_LECTS: return False
    return True

# CS courses from populate_db (5 lectures × 4 sessions + 5 labs × 2 sessions = 30)
CS_COURSES = [
    ('OS','Lecture',4),('DAA','Lecture',4),('SE','Lecture',4),('CMD','Lecture',4),('UI','Lecture',4),
    ('OSL','Lab',2),('DAAL','Lab',2),('SEL','Lab',2),('CMDL','Lab',2),('UIL','Lab',2),
]

# Build session list (same as populate_db)
sessions = []
for code, stype, num_sessions in CS_COURSES:
    for s in range(num_sessions):
        sessions.append({'course':code,'stype':stype,'session':s+1})

# Sort: labs first (same as algorithm)
sessions.sort(key=lambda x: 0 if x['stype']=='Lab' else 1)

print(f"Total sessions to schedule: {len(sessions)}")
print("Order:", [(s['course'],s['stype'],s['session']) for s in sessions])

# Tree data
tree_nodes = [{"id":0,"label":"Start\nB.Tech CS","shape":"box","color":"#17a2b8","font":{"color":"white"}}]
tree_edges = []
gid = 0

assignment = []
grid_events = []  # track grid changes for visualization

def backtrack(sessions, index, assignment, parent_id):
    global gid
    if index >= len(sessions):
        return True

    req = sessions[index]
    slots = LAB_SLOTS if req['stype']=='Lab' else LECTURE_SLOTS

    gid += 1
    cid = gid
    tree_nodes.append({"id":cid,"label":f"Schedule:\n{req['course']} ({req['stype']})","color":"#ffc107"})
    tree_edges.append({"from":parent_id,"to":cid})

    # DEMO MODE: labs start Monday, lectures stagger
    if req['stype']=='Lab':
        sdi=0
    else:
        sdi=index%len(DAYS)
    days = DAYS[sdi:]+DAYS[:sdi]

    for day in days:
        for ts,te in slots:
            ne = {'course':req['course'],'stype':req['stype'],'ts':ts,'te':te,'day':day}
            gid+=1
            tid=gid

            if is_valid(assignment, ne):
                assignment.append(ne)
                tree_nodes.append({"id":tid,"label":f"{day}\n{ts}-{te}","color":"#28a745","font":{"color":"white"}})
                tree_edges.append({"from":cid,"to":tid})
                grid_events.append({"action":"add","day":day,"ts":ts,"te":te,"course":req['course'],"stype":req['stype'],"step":len(grid_events)})

                if backtrack(sessions, index+1, assignment, tid):
                    return True

                # BACKTRACK!
                assignment.pop()
                grid_events.append({"action":"remove","day":day,"ts":ts,"te":te,"course":req['course'],"stype":req['stype'],"step":len(grid_events)})
                gid+=1
                btid=gid
                tree_nodes.append({"id":btid,"label":"Backtracked!\nDead end","color":"#fd7e14","font":{"color":"white"}})
                tree_edges.append({"from":tid,"to":btid})
            else:
                tree_nodes.append({"id":tid,"label":f"Conflict\n{day} {ts}","color":"#dc3545","font":{"color":"white"}})
                tree_edges.append({"from":cid,"to":tid})

    return False

success = backtrack(sessions, 0, assignment, 0)
print(f"\nSuccess: {success}")
print(f"Sessions placed: {len(assignment)}")
print(f"Tree nodes: {len(tree_nodes)}")
print(f"Tree edges: {len(tree_edges)}")

# Count node types
greens = sum(1 for n in tree_nodes if n.get('color')=='#28a745')
reds = sum(1 for n in tree_nodes if n.get('color')=='#dc3545')
oranges = sum(1 for n in tree_nodes if n.get('color')=='#fd7e14')
yellows = sum(1 for n in tree_nodes if n.get('color')=='#ffc107')
print(f"Green(committed): {greens}, Red(conflict): {reds}, Orange(backtrack): {oranges}, Yellow(course): {yellows}")

# Print backtracks
print("\n=== BACKTRACK EVENTS ===")
for e in grid_events:
    if e['action']=='remove':
        print(f"  Backtracked: {e['course']} from {e['day']} {e['ts']}-{e['te']}")

# Print final schedule
print("\n=== FINAL SCHEDULE ===")
for e in sorted(assignment, key=lambda x: (DAYS.index(x['day']), x['ts'])):
    print(f"  {e['day']:10s} {e['ts']}-{e['te']}  {e['course']:5s} ({e['stype']})")

# Write JSON for website
output = {
    "nodes": tree_nodes,
    "edges": tree_edges,
    "grid_events": grid_events,
    "assignment": assignment,
    "stats": {"greens":greens,"reds":reds,"oranges":oranges,"total_sessions":len(assignment)}
}
with open('tree_data.json','w') as f:
    json.dump(output, f, indent=2)
print(f"\nTree data written to tree_data.json ({len(tree_nodes)} nodes)")
