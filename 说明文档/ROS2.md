# 华为官方

## 问题

1. 建图时手推小车正常，但是使用键盘控制小车行动时，小车建图不正常，之前有小车跳变的情况（和里程计有关，因为map可以跳变，但是里程计是连续的不会跳变），现在貌似没看到
   1. 尝试方案
      1. 修改轮距/轮子直径等参数：[Cartographer 建图漂移很利害原因大概找到了 | 鱼香ROS (fishros.org.cn)](https://fishros.org.cn/forum/topic/725/cartographer-建图漂移很利害原因大概找到了/2?lang=zh-CN)------------**有用！！！记得最后保存信息到src文件中**
      2. 板凳固定，雷达稳固，防止抖动
2. 启动定位时，报错时间戳不正常。
   1. 尝试方案
      1. 所有终端使用命令同步时间
      2. 

3. 车起步走的时候会偏向一边
   1. 尝试方案
      1. 将两个电机的位置同步



## 启动

```bash
#vnc连接要用密码 Mind@123，另一个密码只可以看不能操作

#加载控制器
ros2 launch ascend_slam launch_robot.launch.py

#启动激光雷达  /dev/rplidar  --> /dev/ttyUSB0
ros2 launch rplidar_ros view_rplidar_a2m12_launch.py serial_port:=/dev/rplidar frame_id:=laser_frame angle_compensate:=true scan_mode:=Standard baud_rate:=115200

#建图初始化
ros2 launch ascend_slam online_async_launch.py params_file:=/root/asend_slam_ws/install/ascend_slam/share/ascend_slam/config/mapper_params_online_async.yaml use_sim_time:=false

#键盘控制小车移动建图
ros2 run teleop_twist_keyboard teleop_twist_keyboard

#开启定位功能（同时加载了地图）
ros2 launch ascend_slam localization_launch.py map:=/root/ascend_map_save.yaml use_sim_time:=false

#开启导航功能（定位功能包处于开启状态）
ros2 launch ascend_slam navigation_launch.py use_sim_time:=false map_subscribe_transient_local:=true




```



## 安装 

```shell
1.
apt update
apt install -y libegl-mesa0 ros-humble-desktop python3-colcon-common-extensions pip


apt install ros-humble-hardware-interface

apt install ros-humble-twist-mux

apt install ros-humble-controller-manager

apt install ros-humble-diff-drive-controller

apt install ros-humble-joint-state-broadcaster

apt install ros-humble-nav2-common

apt install ros-humble-slam-toolbox

apt install ros-humble-nav2-amcl

apt install ros-humble-nav2-lifecycle-manager




```

以下均为前期试错，不需要看

[ubuntu apt-get install软件安装常见问题解决方法之 Depends: XXX（=YYY） but ZZZ is to be installed_apt : breaks: aptitude (< 0.8.10) but 0.6.8.2-1ubu-CSDN博客](https://blog.csdn.net/chengxiaili/article/details/80190994)



盲猜需要重装humble，源码编译gazebo-ros2-control，出问题的原因应该是 .so根本不存在

先尝试apt isntall  ros-humble-gazebo-ros2-control

https://github.com/ros-controls/gazebo_ros2_control.git   先编译这个试试



安装arm的gazebo

[Gazebo11 on non amd64 : “Open Robotics” team (launchpad.net)](https://launchpad.net/~openrobotics/+archive/ubuntu/gazebo11-non-amd64)

apt install ros-humble-gazebo-dev



安装gazebo_ros

https://github.com/ros-simulation/gazebo_ros_pkgs.git



最后的问题是没有catkinconfig.cmake，怎么安装都不行

## 网站例程

- noetic安装ros_arduino_bridge [ROS_Arduino_bridge/ros_arduino_bridge_Python3/ros_arduino_python/launch/arduino.launch at main · LowPower-Center/ROS_Arduino_bridge (github.com)](https://github.com/LowPower-Center/ROS_Arduino_bridge)



