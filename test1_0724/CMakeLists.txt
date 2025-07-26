cmake_minimum_required(VERSION 3.0.2)
project(test1_0724)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge

)

catkin_package()

catkin_install_python(
  PROGRAMS
    script/test1_0724_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
