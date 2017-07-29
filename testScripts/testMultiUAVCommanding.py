import rospy
import roslaunch
import subprocess
import os
import time
from sensor_msgs.msg import LaserScan, NavSatFix
from std_msgs.msg import Float64;
from gazebo_msgs.msg import ModelStates
from mavros_msgs.msg import State
import sys 
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped,Pose,Vector3,Twist,TwistStamped
from std_srvs.srv import Empty
NUM_UAV=int(sys.argv[1])
cur_pose = PoseStamped()
def pos_cb(msg):
    global cur_pose
    cur_pose = msg

def state_cb(msg):
	if(msg.armed == False):
		print "Standby. Arming!!"
		for uavID in range(0, NUM_UAV):
			try:
                                arm_proxy[uavID](True)
                        except rospy.ServiceException, e:
                                print ("mavros1/set_mode service call failed: %s"%e)

	if(msg.mode != "OFFBOARD"):
		print "Attempting OFFBOARD mode."
		for uavID in range(0, NUM_UAV):
        	        try:
                	        print mode_proxy[uavID](0,'OFFBOARD')
                	except rospy.ServiceException, e:
                        	print ("mavros/set_mode service call failed: %s"%e)
       


local_pos = [None for i in range(NUM_UAV)]
mode_proxy = [None for i in range(NUM_UAV)]
arm_proxy = [None for i in range(NUM_UAV)]
pos_sub = [None for i in range(NUM_UAV)]
start_pos = [None for i in range(NUM_UAV)]
mavros_state = [None for i in range(NUM_UAV)]


def mavrosTopicStringRoot(uavID=0):
    return ('mavros' + str(uavID+1))

startPosX = [5, 4, 4, 2, 3]
startPosY = [0, 0, 0, 2, 3]
startPosZ = [5, 5, 5, 5, 5]

rospy.init_node('multi-', anonymous=True)


for uavID in range(0,NUM_UAV):
    local_pos[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/setpoint_position/local', PoseStamped, queue_size=10)
    mode_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/set_mode', SetMode)
    arm_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/cmd/arming', CommandBool)
    pos_sub[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/local_position/pose', PoseStamped, callback=pos_cb)
    mavros_state[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/state', State, callback=state_cb)

    start_pos[uavID] = PoseStamped()
    start_pos[uavID].pose.position.x = startPosX[uavID]
    start_pos[uavID].pose.position.y = startPosY[uavID]
    start_pos[uavID].pose.position.z = startPosZ[uavID]
    print uavID



#Main method
rate = rospy.Rate(100)
print "Main Running"
while not rospy.is_shutdown():
    for uavID in range(0, NUM_UAV):
    	local_pos[uavID].publish(start_pos[uavID])
	rate.sleep()

