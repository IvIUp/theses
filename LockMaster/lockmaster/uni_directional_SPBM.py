import scheduling_parallel_batching_machines as spbm
import Ships

all_ships = Ships.ships
arrivals_ci = list()

# key: the ship at whose arrival time the block of lock movements started
# value: all the ships that are transfered during that block of lock movements
ships_leaving = {}

# key: job's order number
# value: tuple (job arrival on the c_i, start of job's processing time)
jobs_arrivals_releases = []

# possitions of the machine and their processing times
possitions = []
preprocessing_times = []

# key: departure time
# value: all ships that have left at the departure time
departure_times = {}

# jobs_dict = {ship number : [arrival machine, ending machine, arrival time]}
jobs_dict = {}

# machines_dict = {machine number : [processing time, position]}
machines_dict = {}


def construct_instance():
    starting_machines = []
    ending_machines = []
    with open("jobs.txt", "r") as f:
        for i, job in enumerate(f):
            j = job.split(' ')
            jobs_dict[i + 1] = [int(j[0]), int(j[1]), int(j[2])]
            starting_machines.append(int(j[0]))
            ending_machines.append(int(j[1]))

    commmon_machines = list(range(max(starting_machines), min(ending_machines) + 1))
    if not commmon_machines:
        print("The common machine property is not satisfied among the input jobs and therefore "
              "Uni-directional Scheduling Parallel Batching Machines problem cannot be solved.")
        exit()

    print(f"Common machine(s) = {commmon_machines}")
    commmon_machine = commmon_machines[0]

    with open("machines.txt", "r") as f:
        for i, machine in enumerate(f):
            m = machine.split(' ')
            machines_dict[i + 1] = [int(m[0]), int(m[1])]
            possitions.append(machines_dict[i + 1][1])
            preprocessing_times.append(machines_dict[i + 1][0])

    # Calculate arrival times of all jobs for the common machine c_i
    arrival_times_ci = []
    for order, key in enumerate(jobs_dict):
        preprocessing_time = 0
        possitions_cost = 0
        # print("ship =", key, "arrival time =", jobs_dict[key][2], "starting machine =", jobs_dict[key][0], "ending machine =", jobs_dict[key][1])
        # print(f"machine\t|processing time|\tpossition")
        for job in list(range(jobs_dict[key][0], commmon_machine)):
            # print(f"\t{job}\t|\t\t{machines_dict[job][0]}\t\t|\t\t{machines_dict[job][1]}")
            # print("preprocessing_times[job]", preprocessing_times[job])
            preprocessing_time += preprocessing_times[job]
            possitions_cost += possitions[job + 1] - possitions[job]

        arrival_time = preprocessing_time + possitions_cost + jobs_dict[key][2]
        jobs_arrivals_releases.append((jobs_dict[key][2], arrival_time))
        arrival_times_ci.append(arrival_time)
        # print(f"\tsum\t|\t\t{release_time}\t\t|")
        # print()

    arrivals_ci.extend(sorted(arrival_times_ci))
    # print(f"Arravals on the c_i = {arrivals_ci}")

    # Create ships.txt
    with open("..\..\\visualisation\lockmasterApp\data\ships.txt", "w+") as f:
        # with open("ships.txt", "w+") as f:
        f.write(f"{machines_dict[commmon_machine][0]}\n")
        f.write(f"{len(jobs_dict)}\n")
        for release in sorted(arrival_times_ci):
            f.write(f"{release}, {1}\n")


def extend_solution():
    release_times_ci()
    backtrack_new_release_times()


def backtrack_new_release_times():

    # List of all arrival times and all processing times for all ships
    # (arrival on s_j, starting in s_j, arrival on c_i, starting in c_i)
    new_release_times_sj = []
    for times in jobs_arrivals_releases:
        for release in list(departure_times.keys()):
            if times[1] <= release:
                new_release_times_sj.append((times[0], release - times[1] + times[0], times[1], release))
                break

    # Calculate finish times of all jobs starting on the new relese time
    finish_times = []
    for order, key in enumerate(jobs_dict):
        preprocessing_time = 0
        possitions_cost = 0
        # print(f"machine\t|processing time|\tpossition")
        for machine in list(range(jobs_dict[key][0], jobs_dict[key][1] + 1)):
            # print(f"\t{machine}\t|\t\t{machines_dict[machine][0]}\t\t|\t\t{machines_dict[machine][1]}")
            preprocessing_time += machines_dict[machine][0]
            if machine != jobs_dict[key][1]:
                possitions_cost += machines_dict[machine + 1][1] - machines_dict[machine][1]

        finish_time = preprocessing_time + possitions_cost + new_release_times_sj[order][1]
        finish_times.append(finish_time)

    for order, (time, finish) in enumerate(zip(new_release_times_sj, finish_times)):
        print(f"Ship {order + 1} with arrival on machine {jobs_dict[order + 1][0]} at time {time[0]} has starting time in {time[1]}, and complition time {finish} on machine {jobs_dict[order + 1][1]}.")


def release_times_ci():
    shorthes = spbm.sp[0]
    for i, path in enumerate(shorthes):

        if i == 0 or i == len(shorthes) - 1:
            continue
        else:
            splits = path.split("_")
            ships_order_number = int(splits[0])
            values = []
            if ships_order_number not in list(ships_leaving.keys()):
                for s in arrivals_ci:
                    if s <= all_ships[ships_order_number - 1].arrival_time:
                        values.append(s)
                    else:
                        break

                ships_leaving[ships_order_number] = values
                for arrival_time in ships_leaving[ships_order_number]:
                    arrivals_ci.remove(arrival_time)

            if i == len(shorthes) - 2 and len(arrivals_ci) > 0:
                values = ships_leaving[ships_order_number]
                values.extend(arrivals_ci)
                ships_leaving[ships_order_number] = values

    for d_items in ships_leaving.items():
        departures = d_items[1]

        if len(departures) > 1:
            # If there are some ships that have not been transfered with previous lock movement
            # and are now waiting to be transfered within the next block
            block_duration = departures[-1] - departures[0]
            if len(departure_times) >= 2 and max(d_items[1]) - 4 * Ships.T >= list(departure_times.keys())[-1]:
                lock_movement_time = list(departure_times.keys())[-1] + 2 * Ships.T
                while len(departures) > 0 and lock_movement_time <= departures[-1]:
                    departurings = []
                    for dept in departures:
                        if dept <= lock_movement_time:
                            departurings.append(dept)
                        else:
                            break

                    departure_times[lock_movement_time] = departurings
                    del departures[0: len(departurings)]
                    lock_movement_time += 2 * Ships.T

                    if len(departures) > 0:
                        departure_times[lock_movement_time] = departures

            # If there is a huge block of lock movements
            # i.e. a lot of ships are transfered during this block lock movements
            elif block_duration >= 4 * Ships.T:
                lock_movement_time = departures[0]

                while len(departures) > 0 and lock_movement_time <= departures[-1]:
                    departurings = []
                    for dept in departures:
                        if dept <= lock_movement_time:
                            departurings.append(dept)
                        else:
                            break

                    departure_times[lock_movement_time] = departurings
                    del departures[0: len(departurings)]
                    lock_movement_time += 2 * Ships.T

                if len(departures) > 0:
                    departure_times[lock_movement_time] = departures

            else:
                departure_times[departures[-1]] = departures

        else:
            departure_times[departures[0]] = departures


if __name__ == '__main__':
    construct_instance()
    spbm.lockmaster()  # polynomial time algorithm O(n^3)
    extend_solution()
