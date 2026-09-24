# Warehouse Mapping and Navigation in NVIDIA Isaac Sim

This a small robotics side project built in Fall 2026. It was built in **NVIDIA Isaac Sim** using **ROS 2** to explore 3D LiDAR mapping, autonomous navigation with **Nav2**, and camera-based object detection with **YOLO**.

The main [demo](https://drive.google.com/file/d/1py-F3hPrc_rktvgLoeuulcNFsvTF1PYC/view?usp=sharing) is a warehouse mapping pipeline that accumulates 3D LiDAR scans while a mobile robot moves through the environment. 

I also experimented with Nav2 goal-based navigation and YOLO inference on the robot camera as separate parts. I hope to discuss some of the steps I took in this repo.

# Overview

The project uses a simulated mobile robot in an Isaac Sim warehouse environment with:
- 2D LiDAR
- 3D LiDAR
- RGB camera
- odometry
- TF transforms
- ROS 2 navigation tools

The main ROS 2 topics used included:
```text
/front_2d_lidar/scan
/front_3d_lidar/lidar_points
/chassis/odom
/tf
/cmd_vel
/warehouse_cloud
```

# 3D LiDAR Warehouse Mapping

The main part of the project was reconstructing the warehouse environment using accumulated 3D LiDAR point clouds.

The robot publishes raw 3D LiDAR measurements through: /front_3d_lidar/lidar_points

Each scan only represents what the LiDAR sees from the robot's current position.

To build a larger representation of the warehouse, the scans are transformed into a common odom coordinate frame using the robot's odometry and TF transforms.

This allows measurements collected from different robot positions to remain aligned in the same coordinate frame.

As the robot moves through the warehouse, more of the environment becomes visible and is incorporated into the point cloud.

## Mapping

The robot was manually driven through the simulated warehouse using ROS 2 teleoperation.

As it moved, the 3D LiDAR continuously scanned:
- walls
- obstacles
- floor geometry
- surrounding warehouse structures

The accumulated point cloud was visualized in RViz using:
```text
Fixed Frame: odom
Topic: /warehouse_cloud
```

The result is a progressively reconstructed 3D representation of the warehouse.

## Point Cloud Assembly

I used the ROS 2 'rtabmap_util' point cloud assembler.

Example command that I tuned:
```text
ros2 run rtabmap_util point_cloud_assembler \
  --ros-args \
  -p use_sim_time:=true \
  -p fixed_frame_id:=odom \
  -p assembling_time:=2.0 \
  -p voxel_size:=0.05 \
  -r cloud:=/front_3d_lidar/lidar_points \
  -r odom:=/chassis/odom \
  -r assembled_cloud:=/warehouse_cloud
```

Important parameters:
- fixed_frame_id:=odom
  - places each LiDAR scan into a consistent world-relative frame
- assembling_time:=2.0
  - combines scans over a short time interval
- voxel_size:=0.05
  - downsamples nearby points to reduce point-cloud density
 
The resulting point cloud is published to: "/warehouse_cloud"

## ROS 2 Teleoperation

For the warehouse mapping demo, the robot was driven manually using:
```text
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The teleoperation node publishes velocity commands to the robot through: "/cmd_vel"

# Nav2 Navigation

I also experimented with the ROS 2 Navigation Stack (Nav2) in the same simulated environment.

Nav2 provides the components needed for autonomous mobile robot navigation, including:
- global path planning
- local trajectory control
- obstacle avoidance
- costmaps
- goal execution

The general navigation pipeline is:

I configured the robot so that navigation goals could be sent through RViz using: "2D Goal Pose" or through the ROS 2 navigation action: "/navigate_to_pose"

Nav2 then generated a path and used the robot's sensor data and costmaps to move toward the target.

# YOLO Camera Inference

Separately, I tested YOLO object detection using images from the robot's simulated RGB camera.

The inference script (attached to this repo) subscribes to camera frames, runs YOLO inference, and identifies objects visible from the robot.

