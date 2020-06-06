from math import sqrt
from collections import deque

# Physical constraints (* 20cm is the actual size)
HOLD_RANGE = 10
HUMAN_SIZE = 8.5

# Size of the Moon Board(+ Foot Hold)
HEIGHT_NUM = 20
WIDTH_NUM = 11
culc_dist_map = {}

# Parameters
D_ATTACH = 50
D_FREE = 200
D_TOO_CLOSE = 50
D_UNSTABLE = 95
C_2LIMBS = 120
C_UNSTABLE = 500
C_FREE_HAND = 250
C_FREE_FOOT = 125 # 20
C_HAND_MATCH = 100
C_FOOT_MATCH = 300
C_CROSSING = 100
C_TOO_CLOSE = 1000
C_FAIL = 100000

# Calculating the distance between holds
def culc_hold_dist(hold1, hold2):
    return sqrt((hold1 % WIDTH_NUM - hold2 % WIDTH_NUM)**2 + (int(hold1 / WIDTH_NUM) - int(hold2 / WIDTH_NUM))**2)

# Calculate the cost of move
def culc_move(current_pose,next_pose):
    move_limbs_flag = [0, 0, 0, 0]
    free_limbs_flag = [0, 0, 0, 0, 0, 0, 0, 0]
    pose_distance = [0, 0, 0, 0]
    for i in range(4):
        if current_pose[i] != -1 and next_pose[i] != -1:
            pose_distance[i] = culc_hold_dist(current_pose[i], next_pose[i])
        if current_pose[i] != next_pose[i]:
            move_limbs_flag[i] = 1
        if current_pose[i] == -1:
            free_limbs_flag[i] = 1
        if next_pose[i] == -1:
            free_limbs_flag[i + 4] = 1
    return move_limbs_flag, free_limbs_flag, pose_distance

# Added if a limb is floating
def h_dist(move_limbs_flag, free_limbs_flag, pose_distance, current_pose):
    cost_dist = 0
    for i in range(4):
        if i == 0:
            cost_dist += pose_distance[i] * 20
        elif i == 1:
            cost_dist += pose_distance[i] * 20
        elif free_limbs_flag[i] != 1 and free_limbs_flag[i + 4] != 1:
            cost_dist += pose_distance[i] * 20
        if free_limbs_flag[i] == 1:
            cost_dist += D_ATTACH
        if free_limbs_flag[i + 4] == 1:
            cost_dist += D_FREE   
    return cost_dist

# def h_2limbs(move_limbs_flag, free_limbs_flag, pose_distance):
#     cost_2limbs = 0
#     if (move_limbs_flag[0] == 1 and move_limbs_flag[3] == 1) and (free_limbs_flag[4] == 0 and free_limbs_flag[7] == 0) and (pose_distance[0] >= D_TOO_CLOSE and pose_distance[3] >= D_TOO_CLOSE):
#         cost_2limbs += C_2LIMBS
#     if (move_limbs_flag[1] != 0 and move_limbs_flag[2] != 0) and (free_limbs_flag[5] == 0 and free_limbs_flag[6] == 0) and (pose_distance[1] >= D_TOO_CLOSE and pose_distance[2] >= D_TOO_CLOSE):
#         cost_2limbs += C_2LIMBS
#     return cost_2limbs

# Add cost when you have both feet in the air
def h_unstable(free_limbs_flag):
    cost_unstable = 0
    if free_limbs_flag[6] + free_limbs_flag[7] == 2:
        cost_unstable = C_UNSTABLE
    return cost_unstable

# Calculate Ce (cost of move) in the paper
def cost_e(move_limbs_flag, free_limbs_flag, pose_distance, current_pose):
    cost_dist = h_dist(move_limbs_flag, free_limbs_flag, pose_distance, current_pose)
    cost_unstable = h_unstable(free_limbs_flag)
    return cost_dist + cost_unstable

# Add cost for each floating limb
def h_free(next_pose):
    cost_free = 0
    if next_pose[0] == -1:
        cost_free += C_FREE_HAND 
    if next_pose[1] == -1:
        cost_free += C_FREE_HAND 
    if next_pose[2] == -1:
        cost_free += C_FREE_FOOT
    if next_pose[3] == -1:
        cost_free += C_FREE_FOOT
    return cost_free

# Cost of the match
def h_match(next_pose):
    cost_match = 0
    if next_pose[0] == next_pose[1]:
        cost_match = C_HAND_MATCH
    if next_pose[2] == next_pose[3]:
        cost_match = C_FOOT_MATCH
    return cost_match

# The cost of crosses and feet higher than hands
def h_crossing(next_pose):
    cost_crossing = 0
    right_hand_width = next_pose[0] % WIDTH_NUM
    left_hand_width = next_pose[1] % WIDTH_NUM
    right_foot_width = next_pose[2] % WIDTH_NUM
    left_foot_width = next_pose[3] % WIDTH_NUM
    if right_hand_width < left_hand_width:
        cost_crossing += C_CROSSING
    if right_foot_width < left_foot_width:
        cost_crossing += C_CROSSING
        
    right_hand_height = int(next_pose[0] / WIDTH_NUM)
    left_hand_height = int(next_pose[1] / WIDTH_NUM)
    right_foot_height = int(next_pose[2] / WIDTH_NUM)
    left_foot_height = int(next_pose[3] / WIDTH_NUM)
    if right_hand_height < right_foot_height:
        cost_crossing += C_CROSSING
    if right_hand_height < left_foot_height:
        cost_crossing += C_CROSSING
    if left_hand_height < right_foot_height:
        cost_crossing += C_CROSSING
    if left_hand_height < left_foot_height:
        cost_crossing += C_CROSSING
    return cost_crossing

# The cost of being too close to hand and foot
def h_too_close(next_pose):
    cost_too_close = 0
    if next_pose[0] != -1:
        for i in range(2):
            if next_pose[i+2] != -1:
                tmp_culc_pose_dist = 1 - culc_hold_dist(next_pose[0],next_pose[i+2]) * 20 / D_TOO_CLOSE
                if tmp_culc_pose_dist > 0:
                    cost_too_close += tmp_culc_pose_dist
    if next_pose[1] != -1:
        for i in range(2):
            if next_pose[i+2] != -1:
                tmp_culc_pose_dist = 1 - culc_hold_dist(next_pose[1],next_pose[i+2]) * 20 / D_TOO_CLOSE
                if tmp_culc_pose_dist > 0:
                    cost_too_close += tmp_culc_pose_dist
    return cost_too_close * C_TOO_CLOSE

# Compute Cn (cost of pose) in the paper
def cost_n(next_pose):
    cost_free = h_free(next_pose)
    cost_match = h_match(next_pose)
    cost_crossing = h_crossing(next_pose)
    cost_too_close = h_too_close(next_pose)
    return cost_free + cost_match + cost_crossing + cost_too_close
    
# cost of A*
def a_star_cost(current_pose, next_pose):
    move_limbs_flag, free_limbs_flag, pose_distance = culc_move(current_pose, next_pose)
    return cost_e(move_limbs_flag, free_limbs_flag, pose_distance, current_pose) + cost_n(next_pose)

# start
def culc_start_pose(next_pose):
    return cost_n(next_pose)

# Calculate the center of the hold.
def culc_center_of_hold(hold1, hold2):
    if hold1 == -1 and hold2 == -1:
        return -1, -1
    elif hold1 == -1:
        return hold2 % WIDTH_NUM, int(hold2 / WIDTH_NUM)
    elif hold2 == -1:
        return hold1 % WIDTH_NUM, int(hold1 / WIDTH_NUM)
    else:
        return (hold1 % WIDTH_NUM + hold2 % WIDTH_NUM) / 2, (int(hold1 / WIDTH_NUM) + int(hold2 / WIDTH_NUM)) / 2

# Calculating handholds and distance to goal
def culc_goal_dist(hold1, hold2):
    x, y = culc_center_of_hold(hold1,hold2)
    if len(goal_hold) == 1:
        return sqrt((x - goal_hold[0] % WIDTH_NUM)**2 + (y - int(goal_hold[0] / WIDTH_NUM))**2)
    else:
        goal_x, goal_y = culc_center_of_hold(goal_hold[0], goal_hold[1])
        return sqrt((x - goal_x)**2 + (y - goal_y)**2)

# Register a route
def regist_route(sum_cost, real_cost, pose):
    tmp_array = [sum_cost, pose[0], pose[1], pose[2], pose[3], real_cost]
    if len(route_array) == 0:
        route_array.append(tmp_array)
    else:
        for i in range(len(route_array)):
            if i == len(route_array) - 1 or route_array[i][0] > sum_cost:
                route_array.insert(i,tmp_array)
                break
    return

# Determining if it's not an impossible position for a human size.
def check_human_size_range(hold_position,hold_num, pose):
    for i in range(3):
        if pose[(hold_position + 1 + i) % 4] != -1 and culc_hold_dist(hold_num, pose[(hold_position + 1 + i) % 4]) > HUMAN_SIZE:
            return False
        elif i == 2:
            return True
    
# Check starting size.
def start_pose_check(pose):
#     check_num = culc_hold_dist(pose[0], pose[1]) <= HOLD_RANGE
    if pose[2] != -1 and pose[3] != -1 and culc_hold_dist(pose[2], pose[3]) > HUMAN_SIZE:
        return False
    
    if pose[2] != -1 and (culc_hold_dist(pose[0], pose[2]) > HUMAN_SIZE or culc_hold_dist(pose[1], pose[2]) > HUMAN_SIZE):
        return False
    
    if pose[3] != -1 and (culc_hold_dist(pose[0], pose[3]) > HUMAN_SIZE or culc_hold_dist(pose[1], pose[3]) > HUMAN_SIZE):
        return False
    
    return True

# Match start (when you start with two hands on one hold)
def single_start_pose(start_hold, course_hold):
    for candidate_holdR in course_hold:
        for candidate_holdL in course_hold:
            if candidate_holdL == candidate_holdR:
                continue
            start_pose = [start_hold[0], start_hold[0], candidate_holdR, candidate_holdL]
            if start_pose_check(start_pose):
                real_cost = culc_start_pose(start_pose)
                start_cost = real_cost + culc_goal_dist(start_hold[0], start_hold[0])
                map_dict[str(start_pose)] = "start"
                regist_route(start_cost, real_cost, start_pose)
    return

# Separate Start (when starting two holds with two hands)
def separate_start_pose(start_hold, course_hold):
    for candidate_holdR in course_hold:
        for candidate_holdL in course_hold:
            if candidate_holdL == candidate_holdR:
                continue
            start_pose = [start_hold[0], start_hold[1], candidate_holdR, candidate_holdL]
            if start_pose_check(start_pose):
                real_cost = culc_start_pose(start_pose)
                start_cost = real_cost + culc_goal_dist(start_hold[0], start_hold[1])
                map_dict[str(start_pose)] = "start"
                regist_route(start_cost, real_cost, start_pose)
            start_pose = [start_hold[1], start_hold[0], candidate_holdL, candidate_holdR]
            if start_pose_check(start_pose):
                real_cost = culc_start_pose(start_pose)
                start_cost = real_cost + culc_goal_dist(start_hold[1], start_hold[0])
                map_dict[str(start_pose)] = "start"
                regist_route(start_cost, real_cost, start_pose)
    return

# Assignment of starting poses
def start_pose(start_hold, course_hold):
    if len(start_hold) == 1:
        single_start_pose(start_hold,course_hold)
    else:
        separate_start_pose(start_hold,course_hold)

# Register a route
def regist_map_and_array(current_cost, current_pose, next_pose):
#     if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
    global goal_array
    real_cost = current_cost + a_star_cost(current_pose,next_pose)
    next_cost = real_cost + culc_goal_dist(next_pose[0],next_pose[1])
    map_dict[str(next_pose)] = str(current_pose)
    regist_route(next_cost, real_cost, next_pose)
    if len(goal_hold) == 1:
        if next_pose[0] == goal_hold[0] and next_pose[1] == goal_hold[0]:
            goal_array = [next_cost, next_pose[0], next_pose[1], next_pose[2], next_pose[3]]
    else: 
        if (next_pose[0] == goal_hold[0] and next_pose[1] == goal_hold[1]) or (next_pose[0] == goal_hold[1] and next_pose[1] == goal_hold[0]):
            goal_array = [next_cost, next_pose[0], next_pose[1], next_pose[2], next_pose[3]]
    return

# A* 
def a_star_search_single():
    current_pose = route_array[0][1:5]
    next_cost = -1
    global goal_array
    next_pose = []
    candidate_footR_dist = candidate_footL_dist = candidate_handR_dist = candidate_handL_dist = 0
    for candidate_hold in course_hold:
        if candidate_hold == -1:
            next_pose = [current_pose[0], current_pose[1], -1, current_pose[3]]
            if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
                regist_map_and_array(route_array[0][5], current_pose, next_pose)
            next_pose = [current_pose[0], current_pose[1], current_pose[2], -1]
            if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
                regist_map_and_array(route_array[0][5], current_pose, next_pose)
            continue
        
        if candidate_hold != current_pose[3]:
            next_pose = [current_pose[0], current_pose[1], candidate_hold, current_pose[3]]
            if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
                candidate_footR_dist = 100
                if current_pose[2] != -1:
                    candidate_footR_dist = culc_hold_dist(current_pose[2], candidate_hold)
                if candidate_footR_dist < HOLD_RANGE or current_pose[2] == -1:
                    if check_human_size_range(2, candidate_hold, current_pose):
                        regist_map_and_array(route_array[0][5], current_pose, next_pose) 
        
        if candidate_hold != current_pose[2]:
            next_pose =[current_pose[0], current_pose[1], current_pose[2], candidate_hold]
            if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
                candidate_footL_dist = 100
                if current_pose[2] != -1:
                    candidate_footL_dist = culc_hold_dist(current_pose[3], candidate_hold)
                if candidate_footL_dist < HOLD_RANGE or current_pose[3] == -1:
                    if check_human_size_range(3, candidate_hold, current_pose):
                        next_pose = [current_pose[0], current_pose[1], current_pose[2], candidate_hold]
                        regist_map_and_array(route_array[0][5], current_pose, next_pose)        

        if candidate_hold in foot_only_hold:
            continue
        
        next_pose =[candidate_hold, current_pose[1], current_pose[2], current_pose[3]]
        if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
            candidate_handR_dist = 100
            if current_pose[0] != -1:
                candidate_handR_dist = culc_hold_dist(current_pose[0], candidate_hold)
            if candidate_handR_dist < HOLD_RANGE or current_pose[0] == -1:
                if check_human_size_range(0, candidate_hold, current_pose):
                    regist_map_and_array(route_array[0][5], current_pose, next_pose)               
        
        next_pose = [current_pose[0], candidate_hold, current_pose[2], current_pose[3]]
        if str(next_pose) not in map_dict and str(next_pose) not in past_map_dict:
            candidate_handL_dist = 100
            if current_pose[1] != -1:
                candidate_handL_dist = culc_hold_dist(current_pose[1], candidate_hold)
            if candidate_handL_dist < HOLD_RANGE or current_pose[1] == -1:
                if check_human_size_range(1, candidate_hold, current_pose):
                    regist_map_and_array(route_array[0][5], current_pose, next_pose)
                    
    past_map_dict[str(current_pose)] = route_array[0][0]
    route_array.popleft()
    return

def culc_all():
    global goal_array
    start_pose(start_hold, course_hold)
    while goal_array[0] == 0  and len(route_array) != 0:
        a_star_search_single()
    if len(route_array) == 0:
        print("I couldn't solve!")
        return False
    else:
        goal_pose = goal_array[1:5]
        goal_route = [str(goal_pose)]
        start_flag = ""
        while True:
            start_flag = map_dict[goal_route[-1]]
            goal_route.append(map_dict[goal_route[-1]])
            if start_flag == "start":
                break
        show_route = []
        for pose_state in goal_route:
            if pose_state != "start":
                tmp_pose_array = list(map(int, pose_state[1:-1].split(',')))
                show_route.append(list(map(num_to_hold_convert, tmp_pose_array)))
        show_route.reverse()
        return show_route

foot_only_hold = [1,3,5,7,9,12,14,16,18,20,-1]


def search_algorithm(course_info):
    global start_hold, course_hold, goal_hold, goal_array, map_dict, past_map_dict, route_array
    map_dict = {}
    past_map_dict = {}
    route_array = deque()
    goal_array = [0,0,0,0,0]
    start_hold = course_info[0]
    goal_hold = course_info[1]
    course_hold = course_info[2]
    culc_result = culc_all()
    if culc_result != False:
        print("--------------------  Start !  --------------------")
        for tmp_pose in culc_result:
            print('Left Hand: {0}, Right Hand: {1}, Left Foot: {2}, Right Foot: {3}'.format(tmp_pose[1], tmp_pose[0],tmp_pose[3], tmp_pose[2]))
        print("--------------------  Goal !  ---------------------")
        
charcter_dic = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9, "K": 10}
num_dic = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G", 7:"H", 8:"I", 9:"J", 10:"K"}

def hold_to_num_convert(hold):
    return (int(hold[1:]) + 1) * 11 + charcter_dic[hold[0]]

def num_to_hold_convert(hold):
    if hold == -1:
        return "None"
    elif hold < 22:
        return "Foot Hold"
    else:
        return str(num_dic[hold % WIDTH_NUM])+str(int(hold / WIDTH_NUM) - 1)
    return 

def main():
    print("Please use letters and numbers and leave a space for each hold. Example: A12 B31")
    print("Enter start holds")
    input_start =  list(input().split())
    print("Enter holds other than the start and goal")
    input_course = list(input().split())
    print("Enter goal holds")
    input_goal =  list(input().split())
    print()
    start_hold, course_hold, goal_hold = list(map(hold_to_num_convert, input_start )), list(map(hold_to_num_convert, input_course)), list(map(hold_to_num_convert, input_goal))
    foot_hold = [1,3,5,7,9,12,14,16,18,20,-1]
    course_hold = course_hold + start_hold + goal_hold + foot_hold
    course_info = [start_hold, goal_hold, course_hold]
    search_algorithm(course_info)

if __name__ == "__main__":
    main()
