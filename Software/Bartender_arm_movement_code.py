import math
import time
import logging
import threading
from dataclasses import dataclass, replace

try :
    import serial  # pip install pyserial if you dont have the module 
    
except ImportError:
    serial = None

log = logging.getLogger("bartender")

# ===== CONFIGURATION ====
SERIAL_PORT = "/dev/serial0"    # Wired to TX/RXpins on Raspberry Pi
BAUD = 115200                    # the speed of the connection , got it on the Arduino code 
SEND_INTERVAL = 0.030            # amount of seconds between the signals  


# --- arm geometry (mm) ---
L1 = 360        
L2 = 345        
TOOL_LEN = 50 
ELBOW_UP = True

# --- joints: base(X), shoulder(Y), elbow(Z), wrist(A) ---
# These are the Inverse Kinematics-frame degrees and HOME_Q is the starting point when we turn the arm on .
HOME_Q = (0.0, 90.0, -150.0, 60.0)          # we need to set this
JOINT_SIGN = (1, 1, 1, 1)                   # if we are wanting it to go in the opposite direction make it -1
JOINT_LIMITS = [(-360, 360), (-180, 180), (-180, 180), (-180, 180)] 

# Output of the motors that we will need to change in testing 
MAX_SPEED = (25.0, 12.0, 25.0, 30.0)
MAX_ACCEL = (30.0, 15.0, 30.0, 40.0)
SMOOTH_TIME = 0.5     
SETTLE_TIME = 0.8    

# --- gripper ---
GRIPPER_ENABLED = True   
GRIP_OPEN = 140           
GRIP_CLOSED = 70          
GRIP_TIME = 1.2 
GRIP_MIRROR = (False, False, False)           
CARRY_SCALE = 0.6     # slows the arm down when the cup has the liquid in it 
PRECISE_SCALE = 0.4   # slows the arm down when the arm is picking up the cup , dispenses the shot and giving the customers their order   

# ---- positions ----

@dataclass(frozen=True)
class Pose:
    x: float      
    y: float
    z: float
    pitch: float  

def offset(p, dx=0.0, dy=0.0, dz=0.0, pitch=None):
    return replace(p, x=p.x + dx, y=p.y + dy, z=p.z + dz, pitch=p.pitch if pitch is None else pitch)

CUP_PICK = Pose(300, -200, -100, -90)        
CUP_CLEARANCE = 50  

DISPENSERS = {
    "passion_fruit":   Pose(330, 120, 230, 90),
    "pomegranate":     Pose(330,  40, 230, 90),
    "blueberry":     Pose(330, -40, 230, 90),
    "watermelon": Pose(330, -120, 230, 90),
    "cranberry": Pose(330, 170, 230, 90),
}
PRESS_TRAVEL = 25.0     # distance the arm needs to press up to dispense the shot 
DISPENSE_DWELL = 1.5    # time it takes for shot to be dispense
DISPENSER_DROP = 80.0   # distance arm needs to be below dispensers to move safely 

MIXERS = {"sprite": Pose(250, 220, 200, 90)}
MIXER_PRESS = {"sprite": (0, -20, 0)} 
MIXER_FILL_TIME = {"sprite": 4.0}              

HANDOVER = Pose(300, 0, 80, 90)                
HANDOVER_WAIT = 6.0                           

#----- recipes -----
RECIPES = {
    # name: cordial [(dispenser, shots)], mixer
    "Passion_fruit_Paradise":    {"Cordial": [("passion_fruit", 1)], "mixer": "sprite"},
    "Pomegranate_Punch":         {"Cordial": [("pomegranate", 1)],   "mixer": "sprite"},
    "Blueberry_Bliss":           {"Cordial": [("blueberry", 1)],   "mixer": "sprite"},
    "Cranberry_Crush":           {"Cordial": [("cranberry", 1)], "mixer": "sprite"},
    "Watermelon_Wonder":         {"Cordial": [("watermelon", 1)], "mixer": "sprite"},
}

# == KINEMATICS ==
def ik(p: Pose):
    base = math.degrees(math.atan2(p.y, p.x))
    r = math.hypot(p.x, p.y)
    ph = math.radians(p.pitch)
    wr = r - TOOL_LEN * math.cos(ph)        
    wz = p.z - TOOL_LEN * math.sin(ph)
    c2 = (wr * wr + wz * wz - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(c2) > 1.0:
        raise ValueError(f"Pose {p} is out of reach")
    q2 = math.acos(c2) * (-1 if ELBOW_UP else 1)
    q1 = math.atan2(wz, wr) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    q1d, q2d = math.degrees(q1), math.degrees(q2)
    q3 = p.pitch - (q1d + q2d)              
    return [base, q1d, q2d, q3]

def fk(q):
    base, q1, q2, q3 = q
    a1, a12 = math.radians(q1), math.radians(q1 + q2)
    pitch = q1 + q2 + q3
    ph = math.radians(pitch)
    r = L1 * math.cos(a1) + L2 * math.cos(a12) + TOOL_LEN * math.cos(ph)
    z = L1 * math.sin(a1) + L2 * math.sin(a12) + TOOL_LEN * math.sin(ph)
    b = math.radians(base)
    return Pose(r * math.cos(b), r * math.sin(b), z, pitch)


# == MOTION PROFILE ==
def s_curve(dist, vmax, amax, dt, smooth):
    ta = vmax / amax
    if dist < vmax * ta:                    
        ta = math.sqrt(dist / amax)
        vpk, tc = amax * ta, 0.0
    else:
        vpk, tc = vmax, (dist - vmax * ta) / vmax
    total = 2 * ta + tc
    n = max(2, int(total / dt) + 1)
    v = []
    for i in range(n):
        t = i * dt
        if t < ta:
            v.append(amax * t)
        elif t < ta + tc:
            v.append(vpk)
        else:
            v.append(max(0.0, vpk - amax * (t - ta - tc)))
    w = max(1, int(smooth / dt))
    v = [0.0] * (w - 1) + v + [0.0] * w
    sm = [sum(v[i:i + w]) / w for i in range(len(v) - w + 1)]
    out, acc = [], 0.0
    for x in sm:
        acc += x
        out.append(acc)
    return [o / acc for o in out]


class Aborted(Exception):
    pass


# == ARM ==
class Arm:
    def __init__(self, port=SERIAL_PORT):
        self.port = port
        self.ser = None
        self.q = list(HOME_Q)
        self.stop_event = threading.Event()
        self.grip = GRIP_OPEN  

    # ---- serial ----
    def connect(self):
        if serial is None :
            raise RuntimeError("pip install pyserial")
        self.ser = serial.Serial(self.port, BAUD, timeout=0.05)
        time.sleep(2.0)                     
        self.ser.reset_input_buffer()
        self.send(self.q)                  
        
    def close(self):
        if self.ser:
            self.ser.close()

    def to_firmware(self, q):                                   
        out = []
        for i in range(4):
            lo, hi = JOINT_LIMITS[i]
            if not lo <= q[i] <= hi:
                raise ValueError(f"Joint {i} angle {q[i]:.1f} outside limits {lo}..{hi}")
            out.append(round(JOINT_SIGN[i] * (q[i] - HOME_Q[i])))
        return out

    def send(self, q):
        servos = [int(round(180 - self.grip)) if m else int(round(self.grip)) for m in GRIP_MIRROR]
        line = " ".join(str(a) for a in self.to_firmware(q) + servos) + "\n"
        self.ser.write(line.encode())       
        self.ser.reset_input_buffer()         

    # ---- Motion path ----
    
    def run(self, path, speed_scale=1.0):
        N = 60
        pts = [path(i / N) for i in range(N + 1)]
        for p in pts:
            self.to_firmware(p)          
        lengths = [sum(abs(pts[k + 1][j] - pts[k][j]) for k in range(N)) for j in range(4)]
        lead = max(range(4), key=lambda j: lengths[j] / MAX_SPEED[j])
        if lengths[lead] < 0.3:
            self.send(pts[-1])
            self.q = pts[-1]
            return
        prof = s_curve(lengths[lead], MAX_SPEED[lead] * speed_scale,
                       MAX_ACCEL[lead] * speed_scale, SEND_INTERVAL, SMOOTH_TIME)
        t0 = time.monotonic()
        for k, s in enumerate(prof):
            if self.stop_event.is_set():
                raise Aborted()
            q = path(s)
            self.send(q)
            self.q = q
            delay = t0 + (k + 1) * SEND_INTERVAL - time.monotonic()
            if delay > 0:
                time.sleep(delay)
        self.hold(SETTLE_TIME)

    def hold(self, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if self.stop_event.is_set():
                raise Aborted()
            time.sleep(0.02)

    def move_joints(self, q_target, speed_scale=1.0):
        q0 = list(self.q)
        self.run(lambda s: [a + (b - a) * s for a, b in zip(q0, q_target)], speed_scale)

    def move_to(self, p: Pose, speed_scale=1.0):
        a = fk(self.q)
        self.run(lambda s: ik(Pose(a.x + (p.x - a.x) * s, a.y + (p.y - a.y) * s,
                                a.z + (p.z - a.z) * s,a.pitch + (p.pitch - a.pitch) * s)), speed_scale)

    def gripper(self, closed: bool):
        angle = GRIP_CLOSED if closed else GRIP_OPEN
        log.info("gripper %s -> %d deg", "CLOSE" if closed else "OPEN", angle)
        if not GRIPPER_ENABLED:
            self.hold(GRIP_TIME)
            return
        start = self.grip
        steps = max(1, int(GRIP_TIME / SEND_INTERVAL))
        t0 = time.monotonic()
        for k in range(1, steps + 1):
            if self.stop_event.is_set():
                raise Aborted()
            self.grip = start + (angle - start) * k / steps
            self.send(self.q)
            delay = t0 + k * SEND_INTERVAL - time.monotonic()
            if delay > 0:
                time.sleep(delay)
        self.hold(0.2)   
# =========================================================== DRINK LOGIC ==
class Bartender:
    def __init__(self, arm: Arm, status=lambda m: None):
        self.arm, self.status = arm, status

    def make_drink(self, name,with_mixer=True):
        if name not in RECIPES:
            raise KeyError(f"Unknown drink: {name}")
        r = RECIPES[name]
        a = self.arm
        a.stop_event.clear()
        try:
            self.status("Collecting cup")
            self.pick_up_cup()
            for Cordial, shots in r["Cordial"]:
                self.status(f"Dispensing {Cordial} x{shots}")
                self.shot(Cordial, shots)
            if with_mixer and r["mixer"]:
                self.status(f"Adding {r['mixer']}")
                self.mixer(r["mixer"])
            self.status("Serving")
            self.hand_over()
        finally:
            self.status("Returning home")
            a.move_joints(list(HOME_Q), 1.0) if not a.stop_event.is_set() else None

    def pick_up_cup(self):
        a = self.arm
        above = offset(CUP_PICK, dz=CUP_CLEARANCE)
        a.move_to(above)                                  
        a.gripper(False)
        a.move_to(CUP_PICK, PRECISE_SCALE)                
        a.gripper(True)
        a.move_to(above, PRECISE_SCALE)                   
        a.move_to(offset(above, pitch=90), CARRY_SCALE)   

    def shot(self, spirit, shots):
        a, d = self.arm, DISPENSERS[spirit]
        travel = offset(d, dz=-(PRESS_TRAVEL + DISPENSER_DROP))
        a.move_to(travel, CARRY_SCALE)
        for i in range(shots):
            a.move_to(offset(d, dz=-PRESS_TRAVEL), PRECISE_SCALE)   
            a.move_to(d, PRECISE_SCALE)                              
            a.hold(DISPENSE_DWELL)
            a.move_to(offset(d, dz=-PRESS_TRAVEL), PRECISE_SCALE)    # release
        a.move_to(travel, CARRY_SCALE)

    def mixer(self, name):
        a, m = self.arm, MIXERS[name]
        a.move_to(offset(m, dz=-60), CARRY_SCALE)
        a.move_to(m, PRECISE_SCALE)
        a.move_to(offset(m, *MIXER_PRESS[name]), PRECISE_SCALE)   
        a.hold(MIXER_FILL_TIME[name])
        a.move_to(m, PRECISE_SCALE)                             
        a.hold(1.0)                                             
        a.move_to(offset(m, dz=-60), CARRY_SCALE)   

    def hand_over(self):
        a = self.arm
        a.move_to(HANDOVER, CARRY_SCALE)
        a.hold(HANDOVER_WAIT)        
        a.gripper(False)
        a.move_to(offset(HANDOVER, dx=-60, dz=-40), PRECISE_SCALE)   


