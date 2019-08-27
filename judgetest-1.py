import sensor, image, time,pyb
from pyb import ADC,Pin
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
clock = time.clock()


p_out_0 = Pin('P0', Pin.OUT_PP)#设置p_out为输出引脚        低电平逆时针旋转
p_out_1=  Pin('P1', Pin.OUT_PP)#设置p_out为输出引脚         低电平顺时针旋转
p_out_2 = Pin('P2', Pin.OUT_PP)#设置p_out为输出引脚        单次低电平顺时针转一圈     将不要的球分至底盘
p_out_3 = Pin('P3', Pin.OUT_PP)#设置p_out为输出引脚        单次低电平逆时针转一圈     将想要的球送至射球弹仓


p_out_4 = Pin('P4', Pin.OUT_PP)#设置p_out为输出引脚        传给射球单元的黑/白信号引脚
p_out_5 = Pin('P5', Pin.OUT_PP)#设置p_out为输出引脚        传给射球单元的粉色信号引脚


p_in_7= Pin('P7', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻  Pin.PULL_DOWN 输入下拉电阻 根据抽签决定分球颜色
p_in_8= Pin('P8', Pin.IN, Pin.PULL_UP)#设置p_in为输入引脚，并开启上拉电阻  Pin.PULL_DOWN 输入下拉电阻 判断是否开始分球
p_in_9= Pin('P9', Pin.IN, Pin.PULL_UP)#设置p_in为输入引脚，并开启上拉电阻  Pin.PULL_DOWN 输入下拉电阻 判断是否开始分球判断射球是否就绪执行分球

p_out_0.high()#设置p_out引脚为高
p_out_1.high()#设置p_out引脚为高
p_out_2.high()#设置p_out引脚为高
p_out_3.high()#设置p_out引脚为高

p_out_4.high()#设置p_out引脚为高 传给射球单元黑/白的信号
p_out_5.high()#设置p_out引脚为高 传给射球单元粉色的信号

color_value=1# 调试黑球
Ready_value=1
judge_value=1
w=0
p=0
t=0
b=0
def find_initpoint():
    adc = ADC("P6") # Must always be "P6".  获取灰度传感器的ADC引脚
    location=(adc.read())    #获取灰度传感器传来的模拟量      OPENMV的模拟量最大值为4095
    while location>1100:
        p_out_0.low()              #低电平逆时针旋转
        location=(adc.read())
        print("location=%f"%location)
    p_out_0.high()
    p_out_1.low()
    pyb.delay(200)
    p_out_1.high()  #步进电机停止旋转


def Senddata_Pink():
    print("pink")
    p_out_3.high()
    #p_out_0.low()  #步进电机停止旋转
    print(p_in_7.value())
    while p_in_7.value()==0:
        p_out_0.high()              #低电平逆时针旋转
        print(p_in_7.value())
    p_out_3.low()  #步进电机停止旋转
    #p_out_3.high()
    #find_initpoint()


def Senddata_up():
    if color_flag==1:
        print("white")
    else:
        print("black")
    p_out_3.high()   #逆时针旋转送球
    #p_out_3.high()  #步进电机停止旋转
    while p_in_7.value()==0:#等待射球就绪
        p_out_0.high()              #低电平逆时针旋转
        print(p_in_7.value())
    p_out_3.low()  #步进电机停止旋转
    find_initpoint()


def Senddata_down():
    print("down")
    p_out_2.low()   #顺时针旋转一圈掉球
    #p_out_2.high()  #步进电机停止旋转
    while p_in_7.value()==0:#等待射球就绪
        p_out_2.high()              #低电平逆时针旋转
    p_out_2.low()  #步进电机停止旋转
    find_initpoint()


def biggest(a,b,c):
    # 先比较a和b
    if a>b:
        maxnum = a
    else:
        maxnum = b
    # 再比较maxnum和c
    if c>maxnum:
        maxnum=c
    return maxnum


find_initpoint()    #自定义函数 确定电机回到原点


#逆时针旋转将球送至射球 顺时针将球抛弃
#所有信号引脚全部高电平为静止 低电平运动

#分球射球逻辑：
#            分球识别颜色
#            识别颜色时 取识别的20次颜色中 三种颜色的最大值作为识别的最终颜色
#            确定颜色后 将确定的颜色信息传递给射球单元
#            射球单元调整炮台角度及转速 准备就绪后 将准备就绪的信号传递给分球结构
#            分球接收到信号执行分球动作

sensor.set_auto_exposure(False,600)     #设置曝光
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_saturation(1)            #设置饱和度


while(True):
    clock.tick()
    img = sensor.snapshot()

    if color_value == 1:
        color_flag=1#白球
    else :
        color_flag=0#黑球

    if judge_value == 1:     #定位就绪开始分球射球
        for c in img.find_circles(threshold = 1000, x_margin = 30, y_margin = 50, r_margin = 40,
            r_min = 40, r_max = 60, r_step = 2):#r_step未明确作用 margin为需要合并的圆的大小及位置
            area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())
            #img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))#识别到的红色圆形用红色的圆框出来
        #area为识别到的圆的区域，即圆的外接矩形框
            statistics = img.get_statistics(roi=area)#像素颜色统计
            #print(statistics)
            #l_mode()，a_mode()，b_mode()是L通道，A通道，B通道的众数。
            if 60<statistics.l_mode()<80 and 50<statistics.a_mode()<80 and -50<statistics.b_mode()<-30:#if the circle is pink
                img.draw_circle(c.x(), c.y(), c.r(), color = (255,0,255))#识别到的粉色圆形用粉色的圆框出来
                p=p+1         #p:检测到的分球数量
                t=t+1
            elif 40<statistics.l_mode()<101 and -15<statistics.a_mode()<25 and -15<statistics.b_mode()<5:#if the circle is white
                img.draw_circle(c.x(), c.y(), c.r(), color = (255, 255, 255))#识别到的白色圆形用白色的圆框出来
                w=w+1         #w:检测到的白球数量
                t=t+1
            elif 0<statistics.l_mode()<20 and -10<statistics.a_mode()<0 and 0<statistics.b_mode()<5:#if the circle is white
                img.draw_circle(c.x(), c.y(), c.r(), color = (0, 0, 255))#识别到的黑色圆形用蓝色的圆框出来
                b=b+1         #b:检测到的黑球数量
                t=t+1
            if color_flag==1 and t>10:#抽签为白色 且检测颜色超过20次
                possible_color=biggest(p,w,b)
                if possible_color==p:
                    Senddata_Pink()
                elif possible_color==w:
                    Senddata_up()
                elif possible_color==b:
                    Senddata_down()
                p=0                     #计数清零
                w=0
                b=0
                t=0
                possible_color=0
            elif color_flag==0 and t>10:#抽签为黑色 且检测颜色超过20次
                if possible_color==p:
                    Senddata_Pink()
                elif possible_color==w:
                    Senddata_down()
                elif possible_color==b:
                    Senddata_up()
                p=0                      #计数清零
                w=0
                b=0
                t=0
                possible_color=0


