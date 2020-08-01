CREATE TABLE video(
id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
device VARCHAR(255),
video_app VARCHAR(255),
camera_options VARCHAR(255),
location_app VARCHAR(255),
video_file VARCHAR(255),
notes VARCHAR(255),
gb float,
fps float,
resolution VARCHAR(255),
lens VARCHAR(255),
camera_mount VARCHAR(255),
vehicle VARCHAR(255),
camera_mount_position VARCHAR(255),
camera_orientation VARCHAR(255),
horizontal_angle float,
vertical_angle float
)
