# The geometrical calculus used for Place Cells

import math
import numpy as np
import pandas as pd
import open3d as o3d
from . import MIN_PLACE_CELL_DISTANCE, ICP_DISTANCE_THRESHOLD, ANGULAR_RESOLUTION, MASK_ARRAY
from ...Robot import NO_ECHO_DISTANCE
from ...Utils import cartesian_to_polar
from ...Memory.EgocentricMemory.Experience import EXPERIENCE_CENTRAL_ECHO


def transform_estimation_cue_to_cue(points1, points2, threshold=ICP_DISTANCE_THRESHOLD):
    """Return the transformation from points1 to points2 using o3d ICP algorithm"""
    # print("Cues 1", cues1)
    # print("Cues 2", cues2)
    # Create the o3d point clouds
    pcd1 = o3d.geometry.PointCloud()
    pcd2 = o3d.geometry.PointCloud()
    # Converting to integers seems to avoid rotation
    pcd1.points = o3d.utility.Vector3dVector(np.array(points1, dtype=int))
    pcd2.points = o3d.utility.Vector3dVector(np.array(points2, dtype=int))
    trans_init = np.eye(4)  # Initial transformation matrix (4x4 identity matrix)
    # Apply ICP
    reg_p2p = o3d.pipelines.registration.registration_icp(
        pcd1, pcd2, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint()
        # Add robust kernel (e.g., TukeyLoss)
        # , loss = o3d.pipelines.registration.TukeyLoss(k=0.2)
    )
    # Compute the similarity
    if len(reg_p2p.correspondence_set) == 0:
        print("ICP no match")
        standard_distance = -1
        mse = -1
    else:
        for i, j in np.asarray(reg_p2p.correspondence_set):
            t = np.sqrt(np.linalg.norm(np.asarray(pcd1.points)[i] - np.asarray(pcd2.points)[j])**2)
            print(f"Match {np.asarray(pcd1.points)[i, 0:2]} - {np.asarray(pcd2.points)[j, 0:2]} = {t:.0f}")
        standard_distance = np.sqrt(np.mean([np.linalg.norm(np.asarray(pcd1.points)[i] - np.asarray(pcd2.points)[j])**2
                       for i, j in np.asarray(reg_p2p.correspondence_set)]))
        print(f"ICP average distance: {standard_distance:.0f}, fitness: {reg_p2p.fitness:.2f}")

        # Check if correspondence_set is empty
        if len(reg_p2p.correspondence_set) == 0:
            print("Correspondence set is empty.")
            return None, None, None

        # Apply the transformation to the source cloud
        pcd1.transform(reg_p2p.transformation)

        # Compute the distances between corresponding points
        correspondence_set = np.asarray(reg_p2p.correspondence_set)
        source_points_transformed = np.asarray(pcd1.points)
        target_points_corresponding = np.asarray(pcd2.points)[correspondence_set[:, 1]]

        distances = np.linalg.norm(
            source_points_transformed[correspondence_set[:, 0]] - target_points_corresponding, axis=1
        )

        # Compute Mean Squared Error (MSE)
        mse = np.sqrt(np.mean(distances ** 2))

        # Compute the proportion of good correspondences
        good_correspondences_ratio = np.mean(distances < threshold)
        # print(f"ICP residual average distance: {mse:.0f}, nb close {good_correspondences_ratio}")

    # Return the resulting transformation
    return reg_p2p, mse  # .transformation


def nearby_place_cell(robot_point, place_cells):
    """Return the id of the place cell within place cell distance if any, otherwise 0"""
    pc_distance_id = {np.linalg.norm(pc.point - robot_point): key for key, pc in place_cells.items()}
    if len(pc_distance_id) > 0:
        min_distance = min(pc_distance_id.keys())
        if min_distance < MIN_PLACE_CELL_DISTANCE:
            return pc_distance_id[min_distance]
    return 0


def point_to_polar_array(point):
    """Return an array representing the angular span of the cue at this point"""
    r, theta = cartesian_to_polar(point)
    return np.roll(MASK_ARRAY * r, round(math.degrees(theta)) // ANGULAR_RESOLUTION)


def resample_by_diff(polar_points, theta_span, r_tolerance=30):
    """Return the array of points where difference is greater that tolerance"""
    # Convert point array to a sorted pandas DataFrame
    polar_points = polar_points.copy()
    df = pd.DataFrame(polar_points, columns=['r', 'theta'])  # .sort_values(by='theta').reset_index(drop=True)

    # The mask for rows where r decreases or will increase next and is not zero
    diff_mask = ((df['r'].diff() < -r_tolerance) | (df['r'].diff() > r_tolerance).shift(-1, fill_value=False)) & \
                (df['r'] > 0)
    diff_points = df[diff_mask]

    # Create a grouping key for streaks of similar r values
    df['group'] = (df['r'].diff().abs() > r_tolerance).cumsum()
    # Theta 0 and 2pi belong to the same group
    # max_group = max(df['group'])
    max_group_mask = (df['group'] == max(df['group']))
    df.loc[max_group_mask, 'theta'] = df.loc[max_group_mask, 'theta'].apply(lambda x: x - 2 * math.pi)
    df.loc[max_group_mask, 'group'] = 0

    # Group by the grouping key and calculate the mean r and theta for each group
    grouped = df.groupby('group').agg(
        {'r': 'mean', 'theta': ['mean', lambda x: x.max() - x.min()]}
    ).reset_index(drop=True)
    grouped.columns = ['r', 'theta', 'span']
    large_group_points = grouped[(grouped['span'] >= theta_span) & (grouped['r'] > 0)
                                 & (grouped['r'] < NO_ECHO_DISTANCE)]
    # print("groups\n", grouped, f"theta_span {theta_span}")

    points_of_interest = pd.concat([diff_points, large_group_points[['r', 'theta']]], ignore_index=True)
    return points_of_interest.sort_values(by='theta').to_numpy()


def compare_place_cells(place_cells):
    """Print a comparison of place cells one to one based on central echoes"""
    if len(place_cells) < 2:
        return

    keys = list(place_cells.keys())
    for i in range(len(place_cells)):
        k1 = keys[i]
        if place_cells[k1].is_fully_observed():
            points1 = [c.point() for c in place_cells[k1].cues if c.type == EXPERIENCE_CENTRAL_ECHO]
            for j in range(i + 1, len(place_cells)):
                k2 = keys[j]
                if place_cells[k2].is_fully_observed():
                    points2 = [c.point() for c in place_cells[k2].cues if c.type == EXPERIENCE_CENTRAL_ECHO]
                    reg_p2p, residual_distance = transform_estimation_cue_to_cue(points1, points2)
                    print("Transformation\n", reg_p2p.transformation)
                    print(f"Compare cell {k1} to cell {k2}: "
                          f"translation: {tuple(-reg_p2p.transformation[0:2,3].astype(int))}, "
                          f"residual distance: {residual_distance:.0f}, fitness: {reg_p2p.fitness:.2f}")