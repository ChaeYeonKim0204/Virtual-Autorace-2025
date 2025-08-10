cmake_minimum_required(VERSION 3.0.2)
project(wego)

set(CMAKE_CXX_STANDARD14)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  sensor_msgs
  move_base_msgs
  actionlib_msgs
)


catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES tf_pkg
#  CATKIN_DEPENDS roscpp rospy
#  DEPENDS system_lib
)



include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)


add_executable(convert_lidar src/convert_lidar.cpp)

target_link_libraries(convert_lidar ${catkin_LIBRARIES})

catkin_install_python(
  PROGRAMS
    scripts/navigation_client.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
