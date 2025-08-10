# #!/usr/bin/env python3
# import rospy
# from nav_msgs.msg import OccupancyGrid
# from geometry_msgs.msg import TransformStamped
# from morai_msgs.msg import EgoVehicleStatus
# import tf2_ros

# class PubTF:
#     def __init__(self):
#         rospy.init_node("ego_tf_broadcast",anonymous=True)
#         self.br = tf2_ros.TransformBroadcaster()
#         self.t = TransformStamped()
#         rospy.Subscriber("/Ego_topic",EgoVehicleStatus, self.callback)
#         self.translation = [-19.0-(-0.19691), 4.5 - (-0.278991), -0.03]  # 변환 값 넣기


#     def callback(self, msg):
#         self.t.header.frame_id = "map"
#         self.t.header.stamp = rospy.Time.now()
#         self.t.child_frame_id = "MoraiInfo"
#         self.t.transform.translation.x = msg.position.x + self.translation[0]
#         self.t.transform.translation.y = msg.position.y + self.translation[1]
#         self.t.transform.translation.z = msg.position.z + self.translation[2]
        
#         self.t.transform.rotation.x = 0.0
#         self.t.transform.rotation.y = 0.0
#         self.t.transform.rotation.z = 0.0
#         self.t.transform.rotation.w = 1.0
        
#         self.br.sendTransform(self.t)

# def main():
#     try:
#         pub_tf=PubTF()
#         rospy.spin()

#     except rospy.ROSInterruptException:
#         pass
    
# if __name__ == '__main__':
#     main()

