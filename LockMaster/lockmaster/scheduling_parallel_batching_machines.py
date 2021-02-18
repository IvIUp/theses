import Ships
import networkx as nx

T = Ships.T
A = Ships.ships
arrivals = Ships.arrival_times
positions = Ships.arrival_positions
sp = []


def find_ak_for_s(curr_ship):
    curr_position = curr_ship.arrival_position
    k = 0

    for i in range(len(A)):
        arrival_time = A[i].arrival_time
        interval_end = curr_ship.arrival_time + T
        if arrival_time < interval_end and A[i].arrival_position != curr_position:
            k += 1
        if arrival_time >= interval_end:
            break

    return k


def calc_cost_leaving_s(curr_ship):
    cost = 0

    for a in A:

        if curr_ship.arrival_time > a.arrival_time and curr_ship.arrival_position == a.arrival_position:
            cost += curr_ship.arrival_time - a.arrival_time
        elif curr_ship.arrival_time + T > a.arrival_time and curr_ship.arrival_position != a.arrival_position:
            cost += curr_ship.arrival_time + T - a.arrival_time

    return cost


def calc_cost_enter_t(curr_ship, poss):
    cost = 0
    all_ships = A.copy()
    del all_ships[0:poss + 1]

    if all_ships:
        for a in all_ships:

            interval_start = curr_ship.arrival_time
            interval_end = curr_ship.arrival_time + 2 * T
            if a.arrival_time >= interval_start:
                while interval_start < A[len(A) - 1].arrival_time:
                    if interval_start < a.arrival_time <= interval_end and curr_ship.arrival_position == a.arrival_position:
                        cost += interval_end - a.arrival_time
                    elif interval_start + T < a.arrival_time <= interval_end + T and curr_ship.arrival_position != a.arrival_position:
                        cost += interval_end + T - a.arrival_time

                    interval_start += (2 * T)
                    interval_end += (2 * T)

    return cost


# This function will find subscript l (number of ships arriving at positiom 1 - p(b))
# of node b_l in layer L(b) for block1 and block2
def block_bl(t_a, t_b, block):
    b_l = 0
    block_length = block[2]
    for i in range(len(A)):

        if block_length > 1:
            if t_a.arrival_time + (block_length - 1) * T < arrivals[i] <= t_b.arrival_time + T and positions[i] != t_b.arrival_position:
                b_l += 1
        else:
            if t_a.arrival_time < arrivals[i] <= t_b.arrival_time + T and positions[i] != t_b.arrival_position:
                b_l += 1

    return b_l


def block2_cost(a_ship, a_poss, b_ship, block):
    cost = 0
    all_ships = A.copy()
    del all_ships[0: a_poss + 1]
    t_a = a_ship.arrival_time
    t_b = b_ship.arrival_time

    if all_ships:
        for a in all_ships:

            numb_of_lock_movm_left = block[2]

            if a_ship.arrival_position == b_ship.arrival_position:

                if a_ship.arrival_position == a.arrival_position:

                    interval_start = t_a
                    mid_interval = interval_start + 2 * T
                    numb_of_lock_movm_left -= 2
                    interval_end = t_b

                    # Chech if ship's arrival time is before or after interval
                    if interval_end <= a.arrival_time or interval_start >= a.arrival_time:
                        continue

                    cost = calc_cost(a, cost, interval_end, interval_start, mid_interval, numb_of_lock_movm_left, a_ship, b_ship)

                else:
                    interval_start = t_a + T
                    numb_of_lock_movm_left -= 3
                    interval_end = t_b + T

                    if interval_end <= a.arrival_time or interval_start >= a.arrival_time:
                        continue

                    if numb_of_lock_movm_left < 0:
                        mid_interval = interval_start
                    else:
                        mid_interval = interval_start + 2 * T

                    cost = calc_cost(a, cost, interval_end, interval_start, mid_interval, numb_of_lock_movm_left, a_ship, b_ship)

            else:
                if a_ship.arrival_position == a.arrival_position:

                    interval_start = t_a
                    mid_interval = interval_start + 2 * T
                    numb_of_lock_movm_left -= 2
                    interval_end = t_b + T

                    if interval_end <= a.arrival_time or interval_start >= a.arrival_time:
                        continue

                    cost = calc_cost(a, cost, interval_end, interval_start, mid_interval, numb_of_lock_movm_left, a_ship, b_ship)

                else:
                    interval_start = t_a + T
                    numb_of_lock_movm_left -= 3
                    interval_end = t_b

                    if interval_end <= a.arrival_time or interval_start >= a.arrival_time:
                        continue

                    if numb_of_lock_movm_left < 0:
                        mid_interval = interval_start
                    else:
                        mid_interval = interval_start + 2 * T

                    cost = calc_cost(a, cost, interval_end, interval_start, mid_interval, numb_of_lock_movm_left, a_ship, b_ship)

    return cost


# Chech if ship can be transfered within the next lock movement,
# if lock movement is possible within current interval,
# by incrising the number of mid_intervals by 2T until there is no more movements left.
# If there is no more movements left, it means that ship will be moved at the end of the interval.
def calc_cost(a, cost, interval_end, interval_start, mid_interval, numb_of_lock_movm_left, aship, bship):
    while True:

        if numb_of_lock_movm_left <= 0:
            cost += interval_end - a.arrival_time
            break

        if interval_start < a.arrival_time <= mid_interval:
            cost += mid_interval - a.arrival_time
            break

        if numb_of_lock_movm_left > 0:
            if numb_of_lock_movm_left - 2 <= 0 or aship.arrival_position != bship.arrival_position:
                mid_interval += numb_of_lock_movm_left * T
                numb_of_lock_movm_left = 0
            else:
                mid_interval += 2 * T
                numb_of_lock_movm_left -= 2
            continue

    return cost


def create_blocks(a_ship, a_poss, b_poss, block1, block2, g):
    block_lenght = int((A[b_poss].arrival_time - a_ship.arrival_time) / T)
    if a_ship.arrival_time + 2 * T <= A[b_poss].arrival_time and a_ship.arrival_position == A[b_poss].arrival_position:
        if block_lenght % 2 != 0:
            block_lenght -= 1

        block2.append((a_poss + 1, b_poss + 1, block_lenght))
        block2_bl = block_bl(a_ship, A[b_poss], block2[-1])
        # print(str(a_poss + 1) + "_top, " + str(b_poss + 1) + "_" + str(block2_bl) + ", " + str(block2_cost(a_ship, a_poss, A[b_poss], block2[-1])))
        g.add_edge(str(a_poss + 1) + "_top", str(b_poss + 1) + "_" + str(block2_bl), weight=block2_cost(a_ship, a_poss, A[b_poss], block2[-1]))
    elif a_ship.arrival_time + T <= A[b_poss].arrival_time and a_ship.arrival_position != A[b_poss].arrival_position:
        if block_lenght % 2 == 0:
            block_lenght -= 1

        if block_lenght == 1:
            block1.append((a_poss + 1, b_poss + 1, block_lenght))
            b_l = str(b_poss + 1) + "_" + str(block_bl(a_ship, A[b_poss], block1[-1]))
            block1_add_edge(g, a_poss, b_l, block1_cost(a_ship, a_poss, A[b_poss]), a_ship, A[b_poss])
        else:
            block2.append((a_poss + 1, b_poss + 1, block_lenght))
            block2_bl = block_bl(a_ship, A[b_poss], block2[-1])
            # print(str(a_poss + 1) + "_top, " + str(b_poss + 1) + "_" + str(block2_bl)+ ", " + str(block2_cost(a_ship, a_poss, A[b_poss], block2[-1])))
            g.add_edge(str(a_poss + 1) + "_top", str(b_poss + 1) + "_" + str(block2_bl), weight=block2_cost(a_ship, a_poss, A[b_poss], block2[-1]))


def block1_cost(a_ship, a_poss, b_ship):
    cost = 0
    all_ships = A.copy()
    del all_ships[0: a_poss + 1]
    t_a = a_ship.arrival_time
    t_b = b_ship.arrival_time

    if all_ships:
        for a in all_ships:
            if a_ship.arrival_position == a.arrival_position:

                interval_start = t_a
                interval_end = t_b + T

                if interval_start < a.arrival_time <= interval_end:
                    cost += interval_end - a.arrival_time

            else:
                interval_start = t_a + T
                interval_end = t_b

                if interval_start < a.arrival_time <= interval_end:
                    cost += interval_end - a.arrival_time

    return cost


# Add edges for block1
# from a_k, where k = {0, ... , n) to b_l
def block1_add_edge(g, poss, b_l, cost, a_ship, b_ship):
    for i in range(len(A) + 1):
        # cost of block1 edges does change, every edge has different cost, but becouse of how _k is chosen,
        # i.e. it is the number of waiting ships,
        # change in cost will not effect the total waiting time becouse the shortest path
        # will only be able to leave by the right edge,
        # right in respect to the total waiting time
        cost2 = i * (b_ship.arrival_time - a_ship.arrival_time - T)
        print("BLOCK 1: " + str(poss + 1) + "_" + str(i) + ", " + b_l + ", " + str(cost + cost2))
        g.add_edge(str(poss + 1) + "_" + str(i), b_l, weight=cost + cost2)


def create_edges_leaving_s(g, a):
    s_ak_edge = str(a + 1) + '_' + str(find_ak_for_s(A[a]))
    cost_leaving_s = calc_cost_leaving_s(A[a])
    g.add_edge('s', s_ak_edge, weight=cost_leaving_s)


def create_0_cost_edges(g, a, k, a_top):
    a_k = str(a + 1) + '_' + str(k)
    g.add_edge(a_k, a_top, weight=0)


def create_edges_entering_t(g, a, a_top):
    cost_entering_t = calc_cost_enter_t(A[a], a)
    # print(a_top + ' -- > t cost = ' + str(cost_entering_t))
    g.add_edge(a_top, 't', weight=cost_entering_t)


def lockmaster():
    # print("\nLockmaster - Polynomial time algorithm")

    g = nx.DiGraph()  # Create acyclic graph g
    g.add_node('s')
    g.add_node('t')

    blocks1 = []  # List of blocks. Each block is a tuple (start, end, block_lenght)
    blocks2 = []

    for a in range(len(A)):

        a_top = str(a + 1) + '_top'

        # Creating edges entering node t
        create_edges_entering_t(g, a, a_top)

        # Creating edges leaving node s
        create_edges_leaving_s(g, a)

        for k in range(len(A) + 1):

            # Creating 0-cost edges
            create_0_cost_edges(g, a, k, a_top)

            # Creating block1 and block2 edges
            if k > len(A) - 1:
                continue
            else:
                create_blocks(A[a], a, k, blocks1, blocks2, g)

    # Find shortest path
    # dijkstra's complexity - O( V^2 )
    # V = ( n * (n + 2) + 2) -- #rows * #columns + nodes s and t
    paths = nx.all_shortest_paths(g, source='s', target='t', method='dijkstra', weight='weight')
    path_lenght = nx.shortest_path_length(g, source='s', target='t', weight='weight')

    with open("..\..\\visualisation\lockmasterApp\data\shortestPaths.txt", "w") as f:
        f.truncate(0)
        f.write(str(path_lenght) + "\n")
        for p in paths:
            sp.append(p)
            f.write(str(p) + '\n')
            # print('shortest s --> t path ' + str(p) + ' with cost = ' + str(path_lenght))
        f.write(str(blocks2))

####################################################################################################
####################################################################################################
####################################################################################################
