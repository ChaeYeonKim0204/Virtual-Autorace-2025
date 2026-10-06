#!/usr/bin/env python3
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
import actionlib
import math
import os
import rospkg
import pandas as pd
from geometry_msgs.msg import PoseWithCovarianceStamped

# 기본 Maze용 Navigation Client
class NavigationClient_Maze:
    def __init__(self):
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()
        self.goal_list = list()
        
        self.waypoint2 = MoveBaseGoal()
        self.waypoint2.target_pose.header.frame_id = 'map'
        self.waypoint2.target_pose.pose.position.x = 19.89
        self.waypoint2.target_pose.pose.position.y = -9.998
        self.waypoint2.target_pose.pose.orientation.z = 0.015066
        self.waypoint2.target_pose.pose.orientation.w = 0.999886
        self.goal_list.append(self.waypoint2)
        
        self.sequence = 0
        self.start_time = rospy.Time.now()

    def run(self):
        if self.client.get_state() != GoalStatus.ACTIVE:
            self.start_time = rospy.Time.now()
            goal = self.goal_list[self.sequence]
            goal.target_pose.header.stamp = rospy.Time.now()
            self.client.send_goal(goal)

# Road용 Navigation Client
class NavigationClient_Road:
    def __init__(self, waypoint_file):
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()
        self.waypoints = pd.read_csv(waypoint_file)
        self.goal_list = []

        for idx, row in self.waypoints.iterrows():
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose.position.x = row['field.pose.pose.position.x']
            goal.target_pose.pose.position.y = row['field.pose.pose.position.y']
            goal.target_pose.pose.orientation.z = row['field.pose.pose.orientation.z']
            goal.target_pose.pose.orientation.w = row['field.pose.pose.orientation.w']
            self.goal_list.append(goal)

        self.sequence = 0
        self.start_time = rospy.Time.now()

    def run(self):
        if self.client.get_state() != GoalStatus.ACTIVE:
            self.start_time = rospy.Time.now()
            if self.sequence < len(self.goal_list):
                goal = self.goal_list[self.sequence]
                goal.target_pose.header.stamp = rospy.Time.now()
                self.client.send_goal(goal)
                self.sequence += 1

    def stop(self):
        self.client.cancel_all_goals()

# 현재 위치 추종
def get_pose():
    msg = rospy.wait_for_message('/amcl_pose', PoseWithCovarianceStamped)
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    z = msg.pose.pose.orientation.z
    w = msg.pose.pose.orientation.w
    return x, y, z, w

def main():
    rospy.init_node('navigation_switcher')
    default_waypoints = os.path.join(rospkg.RosPack().get_path('wego'), 'waypoints', 'waypoint_1m.csv')
    road_waypoint_file = rospy.get_param('~road_waypoint_file', default_waypoints)

    maze_client = NavigationClient_Maze()
    road_client = NavigationClient_Road(road_waypoint_file)

    rate = rospy.Rate(1)
    target_x = 19.89
    target_y = -9.998
    target_z = 0.015066
    target_w = 0.999886
    change = []

    while not rospy.is_shutdown():
        x, y, z, w = get_pose()
        
        # 특정 좌표를 지나면 Road 클라이언트로 전환
        if abs(x - target_x) <= 1 and abs(y - target_y) <= 1:
            change.append(1)

        if len(change) < 1:
            maze_client.run()
        else:
            rospy.loginfo("Target range reached!")
            road_client.run()

        rate.sleep()

if __name__ == "__main__":
    main()
