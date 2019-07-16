
import drivers
import math
import time
import sys
import RPi.GPIO as GPIO

global l0,l1,l2,l3,l4,p0,B0,p1,B1,b0,b1,ms

tt = 0  
# dir_steper:0or1:  0:down/1:up
dir = 1
ns = 600
ms = -50
msx = -500

p0 = 350
b0 = 0.1
p1 = 350
b1 = 0

l0 = 280
l1=l2=l3=l4=230

class Stepper():
    def __init__(self, pen, pdr, ppl):
        self.pen = pen
        self.pdr = pdr
        self.ppl = ppl
        GPIO.setup([pen,pdr,ppl], GPIO.OUT, initial=0)

    def enable(self):
        GPIO.output(self.pen, 0)

    def disable(self):
        GPIO.output(self.pen, 1)

    def step(self, d):
        GPIO.output(self.pdr,d)
        GPIO.output(self.ppl,1)
        GPIO.output(self.ppl,0)
                
    def rotate(self, d, nstep, cond=lambda:True):
    # def rotate(self, d, nstep, cond=lambda:True):
        self.enable()
        GPIO.output(self.pdr, d)
        i = 0;
        while i<nstep and cond():
#            tau = 0.002   #guoce
            tau = 0.002   #nwl
            GPIO.output(self.ppl,1)
            time.sleep(tau/2)
            GPIO.output(self.ppl,0)
            time.sleep(tau/2)
            i = i + 1
        return i

    def execute(self, d, l):
        GPIO.output(self.pdr, d)
        for i in range(len(l)):
            GPIO.output(self.ppl, 1)
            GPIO.output(self.ppl, 0)
            time.sleep(l[i])

    def execute(self, d, l, cond):
        GPIO.output(self.pdr, d)
        i = 0
        while i < len(l) and cond():
            GPIO.output(self.ppl, 1)
            GPIO.output(self.ppl, 0)
            time.sleep(l[i])
            i = i + 1
        return i

class DualStepper:
    def __init__(self, ena0, dir0, pul0, ena1, dir1, pul1):
        GPIO.setup([ena0, dir0, pul0, ena1, dir1, pul1], GPIO.OUT, initial = 0)
        self.ena0 = ena0
        self.dir0 = dir0
        self.pul0 = pul0
        self.ena1 = ena1
        self.dir1 = dir1
        self.pul1 = pul1

    def rotate(self, nstep0, nstep1, display=True):
        # tau = 0.002
        tau = 0.008
        # Divide the time
        if nstep0 > 0:
            sgn0 = 1
        else:
            sgn0 = 0

        if nstep1 > 0:
            sgn1 = 1
        else:
            sgn1 = 0

        GPIO.output(self.dir0, sgn0)
        GPIO.output(self.dir1, sgn1)
        countdown0 = abs(nstep0)
        countdown1 = abs(nstep1)
        slotsize = max(min(countdown0, countdown1),1)
        # slot0 = countdown0/slotsize
        # slot1 = countdown1/slotsize
        slot0 = math.floor(countdown0/slotsize)
        slot1 = math.floor(countdown1/slotsize)
        # if display:
        #     print('Directions %d %d' % (sgn0, sgn1))
        #     print('Slots %d %d' % (slot0, slot1))
        #     print('Slotssize %d'  % (slotsize))
        #     print('Remaining steps %d %d' % (countdown0, countdown1))
        # Alternate between two motors
        while countdown0 > 0 and countdown1 > 0:
            for i in range(slot0):
#                if display:
#                    print('0')
                countdown0 = countdown0 - 1
                GPIO.output(self.pul0,1)
                time.sleep(tau)
                GPIO.output(self.pul0,0)
                time.sleep(tau)

            for i in range(slot1):
                # if display:
                #     print('1')
                countdown1 = countdown1 - 1
                GPIO.output(self.pul1,1)
                time.sleep(tau)
                GPIO.output(self.pul1,0)
                time.sleep(tau)

##         Remaining steps for motor 0
        while countdown0 > 0:
            # if display:
            #     print('0')
            countdown0 = countdown0 - 1
            GPIO.output(self.pul0,1)
            time.sleep(tau)
            GPIO.output(self.pul0,0)
            time.sleep(tau)

        # Remaining steps for motor 0
        while countdown1 > 0:
            # if display:
            #     print('1')
            countdown1 = countdown1 - 1
            GPIO.output(self.pul0,1)
            time.sleep(tau)
            GPIO.output(self.pul0,0)
            time.sleep(tau)

def a1(p0,B0):
    global l0,l1,l2,l3,l4
    # 计算A点：

    g = (l1*l1-l0*l0/4+p0*p0-l2*l2)/(2*p0*math.cos(B0));
    k = (l0+2*p0*math.sin(B0))/(2*p0*math.cos(B0));
    a = k*k+1;
    b = l0-2*g*k;
    c = g*g+l0*l0/4-l1*l1;
    d = b*b-4*a*c
    ya = (-b-math.sqrt(b*b-4*a*c))/2/a;
    xa = math.sqrt(l1*l1-(ya+l0/2)*(ya+l0/2));

    yb = p0 * math.sin(B0)
    xb = p0 * math.cos(B0)

    l22 = round(math.sqrt((xb-xa)*(xb-xa)+(yb-ya)*(yb-ya)))
    if  l22 == l2:
        pass
    else:
        xa = -math.sqrt(l1*l1-(ya+l0/2)*(ya+l0/2));
    if B0 >= 0:
        a1 = math.atan((ya+l0/2)/xa);
        if xb == xa:
            a2 = math.pi/2
        elif xb > xa:
            a2 = math.atan((p0*math.sin(B0)+l0/2-l1*math.sin(a1))/(p0*math.cos(B0)-l1*math.cos(a1)));
        else:
            a2 = math.pi + math.atan((p0*math.sin(B0)+l0/2-l1*math.sin(a1))/(p0*math.cos(B0)-l1*math.cos(a1)));
    else:
        if xa == 0:
            a1 = -math.pi/2
        elif xa > 0:
            a1 = math.atan((ya+l0/2)/xa);
        else:
            a1 = -math.pi + math.atan((ya+l0/2)/xa);
        if xb == xa:
            a2 = -math.pi/2
        elif xb > xa:
            a2 = math.atan((p0*math.sin(B0)+l0/2-l1*math.sin(a1))/(p0*math.cos(B0)-l1*math.cos(a1)));
        else:
            a2 = math.pi - math.atan((p0*math.sin(B0)+l0/2-l1*math.sin(a1))/(p0*math.cos(B0)-l1*math.cos(a1)));

    # print("a1",int(a1*180/math.pi),"a2",int(a2*180/math.pi))
    return a1                   

def a4(p0,B0):                  
    global l0,l1,l2,l3,l4,a1
    # 计算C点：
    g1 = (l4*l4-l0*l0/4+p0*p0-l3*l3)/(2*p0*math.cos(B0))
    k1 = (l0-2*p0*math.sin(B0))/(2*p0*math.cos(B0))
    aa = 1+k1*k1
    b1 = 2*k1*g1-l0
    c1 = g1*g1+l0*l0/4-l4*l4

    yc = (-b1+math.sqrt(b1*b1-4*aa*c1))/2/aa
    xc = math.sqrt(l4*l4-(yc-l0/2)*(yc-l0/2))
    yb = p0 * math.sin(B0)
    xb = p0 * math.cos(B0)

    l33 = round(math.sqrt((xc-xb)*(xc-xb)+(yc-yb)*(yc-yb)))
    if l33 == l3:
        pass
    else:
        xc = -xc
    
    if B0 >= 0:
        if xc == 0:
            a4 = math.pi/2
        elif xc > 0:
            a4 = math.atan((yc-l0/2)/xc)
        else:
            a4 = math.pi + math.atan((yc-l0/2)/xc)
        if xc == xb:
            a3 = math.pi/2
        elif xc < xb:
            a3 = -math.atan((l4*math.sin(a4)+l0/2-p0*math.sin(B0))/(p0*math.cos(B0)-l4*math.cos(a4)));
        else:
            a3 = math.pi + math.atan((l4*math.sin(a4)+l0/2-p0*math.sin(B0))/(p0*math.cos(B0)-l4*math.cos(a4)));
    else:
        if xc == 0:
            a4 = -math.pi/2
        else:
            a4 = math.atan((yc-l0/2)/xc)
            # a4 = math.pi+math.atan((yc-l0/2)/xc)
        if xc == xb:
            a3 = -math.pi/2
        elif xc < xb:
            a3 = -math.atan((l4*math.sin(a4)+l0/2-p0*math.sin(B0))/(p0*math.cos(B0)-l4*math.cos(a4)));
        else:
            a3 = -math.pi - math.atan((l4*math.sin(a4)+l0/2-p0*math.sin(B0))/(p0*math.cos(B0)-l4*math.cos(a4)));
    
    # print("a3",int(a3*180/math.pi),"a4:",int(a4*180/math.pi))
    return a4

            
class Servo():
    def __init__(self, pin):
        GPIO.setup(pin,GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
    def start(self, d):
        self.pwm.start(d)
    def change(self, d):
        self.pwm.ChangeDutyCycle(d)
    def stop(self):
        self.pwm.stop()


    
class Relay():
    def __init__(self, pin, init=0):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT, initial=init)
        
        def trigger(self,signal):
            GPIO.output(self.pin, signal)
            
class Button():
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN)
        
    def waitforpress(self):
        GPIO.wait_for_edge(self.pin, GPIO.FALLING)
        
    def getinput(self):
        return not GPIO.input(self.pin)
            
class L298():
    def __init__(self,IN1 , IN2, IN3, IN4, f):
        GPIO.setup([IN1,IN2,IN3,IN4], GPIO.OUT, initial=0)
        self.IN1 = GPIO.PWM(IN1, f)
        self.IN2 = GPIO.PWM(IN2, f)
        self.IN3 = GPIO.PWM(IN3, f)
        self.IN4 = GPIO.PWM(IN4, f)

    def start(self, cyclea, cycleb, cyclec, cycled):
        self.IN1.start(cyclea)
        self.IN2.start(cycleb)
        self.IN3.start(cyclec)
        self.IN4.start(cycled)
        
def wubi(p0,b0,p1,b1):    
    p0 = p0
    B0 = math.atan(b0)
    a10 = a1(p0,B0,)
    a40 = a4(p0,B0)
    # print("p0=",p0,"B0=",(B0*180/math.pi))
    # print("a10=",(a10*180/math.pi),"a40=",(a40*180/math.pi))

    # print("P1,B1")
    p0 = p1
    B0 = math.atan(b1)

    a11 = a1(p0,B0)
    a41 = a4(p0,B0)
    # a41 = math.pi-a4(p0,B0)

    # print("p1=",p0,"B1=",(B0*180/math.pi))
    # print("a11=",(a11*180/math.pi),"a41=",(a41*180/math.pi))

    da1 = (a11 -a10)*180/math.pi
    da4 = (a41- a40)*180/math.pi
    # print("da1:",round(da1*100)/100,"da4:",round(da4*100)/100)
    

    step_da1 = round(4*200*da1/360)
    step_da4 = round(4*200*da4/360)
    # step_da1 = round(200*da1/360)
    # step_da4 = round(200*da4/360)
    # print("step_da1",step_da1,"step_da4",step_da4)
    ds.rotate(step_da1, step_da4)
    time.sleep(1)
    return

def bdxz(ms,msx, cond=lambda:True):

    bd_xz.rotate(ms,msx,btnZ.getinput)
    time.sleep(1)
    return

    # work
def work_prepare():
                                    
    # reset
    sj.rotate(dir, 600, btnZ.getinput)    #升起到传感器0位
    bdxz(0,400,btnxz.getinput)  #旋转到可铲饼0位
    bdxz(400,0,btnbd.getinput)  #摆动到鏊子边缘
    t0 = 1    # 实际约120秒
    #鏊子旋转启动
    #鏊子加热启动
    time.sleep(t0)   # t0 鏊子预热时间

def work_one_times():
    t1 = 2; t2 = 3;t3 = 40;t4 = 20; t5 =40
    ns = 800   # ns: 从0位到摊饼位置步数（升降）
    js = 1000   # js: 从0位到铲饼位置步数（升降）
    zns = 200  # zns:展饼所需步数（摆动）
    cns = 100  # cns:铲饼所需步数

    ts =time.time()
    #加油（泵启动）
    time.sleep(t1)   # t1 加油时间
    
    #电磁铁吸起毛刷
    wubi(300,-1,300,0)      #刷匀油
    wubi(300,0,300,-1)      #无边复位
    #电磁铁放下毛刷
    wubi(300,-1,290,-1.2)   # 五边移动到鸡蛋容器处    
    
    bdxz(-100,0)   #摆动到摊饼位置（鏊子中间）
    ks =  sj.rotate(0, ns)    #下降到可摊饼高度
    #加面糊（泵启动）
    time.sleep(t2)   # t2 加面糊时间
    ks1 =  sj.rotate(1, 5)    #下降到可摊饼高度
    time.sleep(3)
    ks2 =  sj.rotate(1, 5)    #下降到可摊饼高度
    time.sleep(3)
    ms = ns - 5 - 5
    ks3 =  sj.rotate(1, ms)    #高度复位
    time.sleep(t3)   # t3 第一面加热时间（加蛋前）
    #加蛋
    ks4 =  sj.rotate(0, ms-10)    #高度复位
    wubi(290,-1.2,300,0)   # 五边加鸡蛋    
    wubi(300,0,290,-1.2)   # 五边复位
    ks5 =  sj.rotate(1, ms-10)    #高度复位
    wubi(290,-1.2,260,-1.4)   # 五边移动到调料处
    time.sleep(t4)   # t4 加单后加热时间 
    bdxz(cns,0)   #摆臂复位,cns:铲饼前进步数
    ks6 =  sj.rotate(0, js)    #降到铲饼高度
    
    bdxz(cns,0)   #铲饼
    bdxz(-0.6*cns,0)   #后撤到卷饼起始位置
    ks6 =  sj.rotate(1, 300)    #升到卷饼高度
    bdxz(zns,800)   #卷饼 ，zns:展饼所需步数
    bdxz(-zns,0)   #后撤至鏊子边缘，待展饼位置
    bdxz(zns,-800)   #展饼
    time.sleep(t5)
    ks6 =  sj.rotate(1, ns-300)    #升到卷饼高度
    bdxz(-zns,0)   #复位
    time.sleep(30)  #等待折叠后移动
    t = time.time()-ts
    print("t",t)
def work_cycle():
    ts = time.time()
    work_prepare()
    for i in range(2):
        print("i",i)
        work_one_times()
        t = time.time()-ts
    with open("data.csv", "a") as logfile:
        logfile.write(time.strftime("%Y-%m-%d-%H-%M-%S"))
        logfile.write(", %d"%i)
        logfile.write(", %d\n"%t)
    t = time.time()-ts
    print("all_time",t)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)

    ds = DualStepper(26,19,13,6,5,0)
    bd_xz = DualStepper(22,27,17,18,15,14)
    sj = Stepper(11,9,10)

    # Buttons

    btnZ = Button(21)
    btnbd = Button(20)
    btnxz = Button(16)

    work_cycle()
    
    GPIO.cleanup()
