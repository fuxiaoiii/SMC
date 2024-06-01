1. [深入理解加速计、陀螺仪和磁力计：3轴、6轴和9轴传感器简介-百度开发者中心 (baidu.com)](https://developer.baidu.com/article/detail.html?id=3021028) 需要先了解右手法则
   1. 加速计：测量物体在三个轴向（即X、Y、Z轴）上的加速度变化
   2. 陀螺仪：检测设备在三个轴向（即X、Y、Z轴）上的**旋转**速度和角度
   3. 磁力计：测量磁场强度和方向

2. **里程计**详解![image-20240503132400576](https://raw.githubusercontent.com/fuxiaoiii/Pictures/main/image-20240503132400576.png)

   1. 包含

      - 小车的实时**速度**

      - 小车的实时**里程计位置**（通过编码器获取速度，通过z速度 * 时间累计得到航向角，通过 速度* 时间 * 航向角 累计得到x y方向的坐标)

   2. 发布 odom -> base_footprint 的tf坐标表换


​    3. [d2l-ros2-foxy/docs/foxy/chapt3/3.5.2使用非OOP方法编写一个节点并测试.md at master · daxiongpro/d2l-ros2-foxy (github.com)](https://github.com/daxiongpro/d2l-ros2-foxy/blob/master/docs/foxy/chapt3/3.5.2使用非OOP方法编写一个节点并测试.md)




1. APP体验

2. 终端控制

   1. 关闭开机自启大程序  [2、关闭开机自启动大程序 (yahboom.com)](https://www.yahboom.com/build.html?id=6513&cid=529)

   2. 使用docker

      1. 启动容器并进入（创建新容器）： ./run_docker.sh

      2. docker run 运行镜像启动容器（创建新容器），eg. docker run -it ubuntu:latest /bin/bash

      3. 查看容器ID  docker ps -a 

      4. **进入容器  docker exec -it e4d041c674f6 /bin/bash**

      5. 提交镜像  docker commit 容器id 要创建的目标镜像名:[标签名]   ；eg. docker commit 66c40ede8c68 yahboomtechnology/ros-foxy:4.0.6

      6. 在容器中  exit  退出并关闭容器  ； crtl + p + q 退出但不关闭容器

      7. ```bash
         docker start (容器id or 容器名)      # 启动容器
         docker restart (容器id or 容器名)    # 重启容器
         docker stop (容器id or 容器名)       # 停止容器
         docker kill (容器id or 容器名)       # 强制停止容器
         
         docker rm 容器id                   # 删除指定容器
         docker rm -f $(docker ps -a -q)   # 删除所有容器
         docker ps -a -q|xargs docker rm   # 删除所有容器
         
         # 删除镜像
         docker rmi -f 镜像id # 删除单个
         docker rmi -f 镜像名:tag 镜像名:tag # 删除多个
         docker rmi -f $(docker images -qa) # 删除全部
         ```

      7. 测试ros2的多机通信 ros2 multicast receive    ros2 multicast send





