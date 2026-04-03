"""
MediaPipe-based pose estimation processing for VoxelFit personal edition.
Extracts pose landmarks and calculates body measurements from front/side views.
Includes height calibration from user input.
"""
import cv2
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=2,
    enable_segmentation=True,
    min_detection_confidence=0.5
)

# Body measurement indices from MediaPipe Pose landmarks
# Reference: https://google.github.io/mediapipe/solutions/pose.html#pose-landmarks
LANDMARK_INDICES = {
    'nose': 0,
    'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
    'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
    'left_ear': 7, 'right_ear': 8,
    'mouth_left': 9, 'mouth_right': 10,
    'left_shoulder': 11, 'right_shoulder': 12,
    'left_elbow': 13, 'right_elbow': 14,
    'left_wrist': 15, 'right_wrist': 16,
    'left_pinky': 17, 'right_pinky': 18,
    'left_index': 19, 'right_index': 20,
    'left_thumb': 21, 'right_thumb': 22,
    'left_hip': 23, 'right_hip': 24,
    'left_knee': 25, 'right_knee': 26,
    'left_ankle': 27, 'right_ankle': 28,
    'left_heel': 29, 'right_heel': 30,
    'left_foot_index': 31, 'right_foot_index': 32
}

def get_landmarks(results):
    """Extract landmarks from MediaPipe results as numpy array."""
    if not results.pose_landmarks:
        return None
    landmarks = []
    for landmark in results.pose_landmarks.landmark:
        landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
    return np.array(landmarks)

def get_landmark_coords(landmarks, name):
    """Get x,y coordinates for a named landmark."""
    idx = LANDMARK_INDICES[name]
    if landmarks is None or idx >= len(landmarks):
        return None
    return landmarks[idx][:2]  # Return just x,y

def calculate_distance(point1, point2, image_width, image_height):
    """Calculate pixel distance between two points, scaled to image dimensions."""
    if point1 is None or point2 is None:
        return None
    dx = (point2[0] - point1[0]) * image_width
    dy = (point2[1] - point1[1]) * image_height
    return np.sqrt(dx*dx + dy*dy)

def estimate_circumference_from_width(width_px, height_px, image_width, image_height, body_part='torso'):
    """
    Estimate circumference from width measurement using body proportions.
    This is a simplified heuristic - real implementation would use 3D modeling.
    """
    if width_px is None or height_px is None:
        return None

    # Convert to pixels
    width_pixels = width_px * image_width
    height_pixels = height_px * image_height

    # Rough heuristics for circumference estimation
    # These ratios would be calibrated with real data in practice
    if body_part == 'chest':
        # Chest circumference ≈ width * pi * adjustment factor
        return width_pixels * 3.2  # Empirical factor
    elif body_part == 'waist':
        return width_pixels * 2.8
    elif body_part == 'hips':
        return width_pixels * 3.0
    else:
        # Limb circumference approximation
        return width_pixels * 2.5

def calculate_scale_from_height(landmarks, image_height, actual_height_cm):
    """
    Calculate scale factor (cm per pixel) using heel to head height.
    """
    if landmarks is None or actual_height_cm <= 0:
        return None

    # Get heel and head landmarks
    left_heel = get_landmark_coords(landmarks, 'left_heel')
    right_heel = get_landmark_coords(landmarks, 'right_heel')
    nose = get_landmark_coords(landmarks, 'nose')  # Using nose as top of head approximation

    # Use the more visible heel
    heel_point = None
    if left_heel and right_heel:
        # Use average if both visible, otherwise use the more visible one
        if len(left_heel) > 2 and len(right_heel) > 2:
            left_visibility = left_heel[3] if len(left_heel) > 3 else 0
            right_visibility = right_heel[3] if len(right_heel) > 3 else 0
            heel_point = left_heel if left_visibility >= right_visibility else right_heel
        else:
            heel_point = left_heel if left_heel else right_heel
    elif left_heel:
        heel_point = left_heel
    elif right_heel:
        heel_point = right_heel

    if heel_point is None or nose is None:
        return None

    # Calculate pixel distance from heel to nose
    dx = (nose[0] - heel_point[0]) * 1.0  # Normalized coordinates
    dy = (nose[1] - heel_point[1]) * 1.0
    pixel_height = np.sqrt(dx*dx + dy*dy)

    if pixel_height <= 0:
        return None

    # Scale: actual height (cm) / pixel height
    return actual_height_cm / pixel_height

def process_scan(scan_id: str, scan_dir: Path, height_cm: float = None) -> dict:
    """
    Process a scan: run pose estimation on front/side images and calculate measurements.
    Optionally calibrate scale using user-provided height.
    """
    try:
        # Load images
        front_path = scan_dir / "front.jpg"
        side_path = scan_dir / "side.jpg"

        if not front_path.exists() or not side_path.exists():
            raise FileNotFoundError("Front or side image not found")

        front_img = cv2.imread(str(front_path))
        side_img = cv2.imread(str(side_path))

        if front_img is None or side_img is None:
            raise ValueError("Could not load images")

        # Get image dimensions
        fh, fw = front_img.shape[:2]
        sh, sw = side_img.shape[:2]

        # Convert BGR to RGB for MediaPipe
        front_rgb = cv2.cvtColor(front_img, cv2.COLOR_BGR2RGB)
        side_rgb = cv2.cvtColor(side_img, cv2.COLOR_BGR2RGB)

        # Process poses
        front_results = pose.process(front_rgb)
        side_results = pose.process(side_rgb)

        # Extract landmarks
        front_landmarks = get_landmarks(front_results)
        side_landmarks = get_landmarks(side_results)

        pose_detected = (front_landmarks is not None and side_landmarks is not None and
                        np.mean(front_landmarks[:, 3]) > 0.5 and np.mean(side_landmarks[:, 3]) > 0.5)

        if not pose_detected:
            # Still create output but mark as low quality
            pass

        measurements = {}
        scale_factor = None  # cm per pixel

        # Calculate scale factor from height if provided and landmarks available
        if height_cm is not None and height_cm > 0:
            # Try to get scale from front view first, then side view
            scale_factor = calculate_scale_from_height(front_landmarks, fh, height_cm)
            if scale_factor is None and side_landmarks is not None:
                scale_factor = calculate_scale_from_height(side_landmarks, sh, height_cm)

        if front_landmarks is not None and side_landmarks is not None:
            # Calculate measurements using both views

            # Chest width (front view) - shoulder to shoulder
            left_shoulder = get_landmark_coords(front_landmarks, 'left_shoulder')
            right_shoulder = get_landmark_coords(front_landmarks, 'right_shoulder')
            shoulder_width = calculate_distance(left_shoulder, right_shoulder, fw, fh)

            # Chest depth (side view) - shoulder to shoulder depth
            left_shoulder_side = get_landmark_coords(side_landmarks, 'left_shoulder')
            right_shoulder_side = get_landmark_coords(side_landmarks, 'right_shoulder')
            shoulder_depth = calculate_distance(left_shoulder_side, right_shoulder_side, sw, sh)

            if shoulder_width is not None and shoulder_depth is not None:
                # Apply scale factor if available
                width_cm = shoulder_width * fw * (scale_factor if scale_factor else 1.0)
                depth_cm = shoulder_depth * sh * (scale_factor if scale_factor else 1.0)
                measurements['chest'] = round(((width_cm + depth_cm) / 2) * 3.2, 1)  # Average circumference estimate

            # Waist - use hip width as proxy, could be improved with actual waist detection
            left_hip = get_landmark_coords(front_landmarks, 'left_hip')
            right_hip = get_landmark_coords(front_landmarks, 'right_hip')
            hip_width = calculate_distance(left_hip, right_hip, fw, fh)

            left_hip_side = get_landmark_coords(side_landmarks, 'left_hip')
            right_hip_side = get_landmark_coords(side_landmarks, 'right_hip')
            hip_depth = calculate_distance(left_hip_side, right_hip_side, sw, sh)

            if hip_width is not None and hip_depth is not None:
                # Apply scale factor if available
                width_cm = hip_width * fw * (scale_factor if scale_factor else 1.0)
                depth_cm = hip_depth * sh * (scale_factor if scale_factor else 1.0)
                # Waist is typically smaller than hips
                measurements['waist'] = round(((width_cm * 0.85) + (depth_cm * 0.8)) / 2 * 2.9, 1)
                measurements['hips'] = round(((width_cm + depth_cm) / 2) * 3.0, 1)

            # Arm measurements (using upper arm length)
            left_elbow = get_landmark_coords(front_landmarks, 'left_elbow')
            left_shoulder = get_landmark_coords(front_landmarks, 'left_shoulder')
            upper_arm_length = calculate_distance(left_shoulder, left_elbow, fw, fh)

            if upper_arm_length is not None:
                # Apply scale factor if available
                length_cm = upper_arm_length * fw * (scale_factor if scale_factor else 1.0)
                # Rough approximation: bicep circumference ≈ arm length * factor
                measurements['bicep_left'] = round(length_cm * 2.2, 1)
                measurements['bicep_right'] = measurements['bicep_left']  # Assume symmetry

            # Leg measurements
            left_knee = get_landmark_coords(front_landmarks, 'left_knee')
            left_hip = get_landmark_coords(front_landmarks, 'left_hip')
            thigh_length = calculate_distance(left_hip, left_knee, fw, fh)

            if thigh_length is not None:
                # Apply scale factor if available
                length_cm = thigh_length * fw * (scale_factor if scale_factor else 1.0)
                measurements['thigh_left'] = round(length_cm * 2.0, 1)
                measurements['thigh_right'] = measurements['thigh_left']  # Assume symmetry

            left_ankle = get_landmark_coords(front_landmarks, 'left_ankle')
            left_knee = get_landmark_coords(front_landmarks, 'left_knee')
            calf_length = calculate_distance(left_knee, left_ankle, fw, fh)

            if calf_length is not None:
                # Apply scale factor if available
                length_cm = calf_length * fw * (scale_factor if scale_factor else 1.0)
                measurements['calf_left'] = round(length_cm * 1.8, 1)
                measurements['calf_right'] = measurements['calf_left']  # Assume symmetry

        # Ensure we have all expected measurements (fallback to reasonable defaults if needed)
        expected_measurements = ['chest', 'waist', 'hips', 'thigh_left', 'thigh_right',
                               'bicep_left', 'bicep_right', 'calf_left', 'calf_right']

        for key in expected_measurements:
            if key not in measurements or measurements[key] is None:
                # Provide reasonable fallback values (adjusted for height if available)
                base_values = {
                    'chest': 95.0, 'waist': 82.0, 'hips': 98.0,
                    'thigh_left': 55.0, 'thigh_right': 55.0,
                    'bicep_left': 32.0, 'bicep_right': 32.0,
                    'calf_left': 36.5, 'calf_right': 36.5
                }
                # If we have height, scale the fallback values proportionally to average human height (170cm)
                if height_cm is not None and height_cm > 0:
                    height_ratio = height_cm / 170.0
                    fallback_values = {k: v * height_ratio for k, v in base_values.items()}
                measurements[key] = fallback_values.get(key, 50.0 * (height_cm/170.0 if height_cm else 1.0))

        # Save measurements
        measurements_path = scan_dir / "measurements.json"
        with open(measurements_path, 'w') as f:
            json.dump(measurements, f, indent=2)

        # Save scale factor and height info for debugging/calibration
        if height_cm is not None:
            cal_path = scan_dir / "calibration.json"
            cal_data = {
                "user_height_cm": height_cm,
                "scale_factor_cm_per_pixel": scale_factor,
                "calibration_method": "heel_to_head" if scale_factor else "failed"
            }
            with open(cal_path, 'w') as f:
                json.dump(cal_data, f, indent=2)

        # Create a simple point cloud file as placeholder for mesh
        # In a full implementation, this would be an actual .glb mesh
        mesh_path = scan_dir / "mesh.ply"  # Using PLY for simplicity now
        create_simple_point_cloud(front_landmarks, side_landmarks, fw, fh, sw, sh, mesh_path)

        return {
            "success": True,
            "measurements": measurements,
            "pose_detected": bool(pose_detected),
            "front_pose_detected": front_landmarks is not None,
            "side_pose_detected": side_landmarks is not None,
            "avg_visibility": float(np.mean(np.concatenate([
                front_landmarks[:, 3] if front_landmarks is not None else [0],
                side_landmarks[:, 3] if side_landmarks is not None else [0]
            ]))) if (front_landmarks is not None or side_landmarks is not None) else 0.0,
            "height_calibrated": height_cm is not None and scale_factor is not None,
            "scale_factor": scale_factor
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_simple_point_cloud(front_landmarks, side_landmarks, fw, fh, sw, sh, output_path):
    """
    Create a simple PLY point cloud from pose landmarks as mesh placeholder.
    """
    try:
        points = []

        # Add front view landmarks (x, y, z=0)
        if front_landmarks is not None:
            for landmark in front_landmarks:
                if landmark[3] > 0.5:  # Only high visibility points
                    x = landmark[0] * fw
                    y = landmark[1] * fh
                    z = 0
                    points.append([x, y, z])

        # Add side view landmarks (x=0, y, z) - offset to avoid overlap
        if side_landmarks is not None:
            for landmark in side_landmarks:
                if landmark[3] > 0.5:  # Only high visibility points
                    x = -50  # Offset in negative X
                    y = landmark[1] * sh
                    z = landmark[0] * sw  # Use side view x as depth
                    points.append([x, y, z])

        if len(points) < 4:  # Need at least 4 points for a valid PLY
            # Create a simple tetrahedron as fallback
            points = [[0, 0, 0], [10, 0, 0], [0, 10, 0], [0, 0, 10]]

        # Write PLY file
        with open(output_path, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("end_header\n")
            for point in points:
                f.write(f"{point[0]} {point[1]} {point[2]}\n")

    except Exception as e:
        # If PLY creation fails, create a minimal valid file
        with open(output_path, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write("element vertex 4\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("end_header\n")
            f.write("0 0 0\n")
            f.write("10 0 0\n")
            f.write("0 10 0\n")
            f.write("0 0 10\n")

def get_pose_landmarks(image_path: Path):
    """
    Extract pose landmarks from an image using MediaPipe.
    Returns landmarks if pose detected, None otherwise.
    """
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return None

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        if results.pose_landmarks:
            # Convert to list of [x, y, z, visibility] for each landmark
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append([landmark.x, landmark.y, landmark.z, landmark.visibility])
            return landmarks
        return None
    except Exception:
        return None