import configparser
import csv
import time
import threading

def merge(low, mid, high):
    left = a[low:mid+1]
    right = a[mid+1:high+1]

    n1 = len(left)
    n2 = len(right)
    i = j = 0
    k = low

    while i < n1 and j < n2:
        if left[i] <= right[j]:
            a[k] = left[i]
            i += 1
        else:
            a[k] = right[j]
            j += 1
        k += 1

    while i < n1:
        a[k] = left[i]
        i += 1
        k += 1

    while j < n2:
        a[k] = right[j]
        j += 1
        k += 1

def merge_sort(low, high):
    if low < high:
        mid = low + (high - low) // 2

        merge_sort(low, mid)
        merge_sort(mid + 1, high)

        merge(low, mid, high)

def merge_sort_threaded(arr):
    global a
    a = arr

    max_elements = len(a)
    global part
    part = 0
    thread_max = 5

    for i in range(thread_max):
        t = threading.Thread(target=merge_sort, args=(part * (max_elements // 4), (part + 1) * (max_elements // 4) - 1))
        part += 1
        t.start()

    for i in range(thread_max):
        t.join()

    merge(0, (max_elements // 2 - 1) // 2, max_elements // 2 - 1)
    merge(max_elements // 2, max_elements // 2 + (max_elements - 1 - max_elements // 2) // 2, max_elements - 1)
    merge(0, (max_elements - 1) // 2, max_elements - 1)

    return a

def read_data_file(file_name, limit):
    """Funkcja odczytuje dane z pliku i zwraca je w odpowiednim formacie."""
    extension = file_name.split('.')[-1]

    if extension == 'csv':
        with open(file_name, newline='') as csvfile:
            data = [list(map(int, row)) for row in csv.reader(csvfile)]
    elif extension == 'txt':
        with open(file_name) as txtfile:
            data = [list(map(int, row.split(', '))) for row in txtfile]
    else:
        raise ValueError("Nieobsługiwany format pliku wejściowego.")
    data = data[0]
    data = data[0:limit]
    return data


def save_results(results, time_elapsed, output_file_name, intput_file_name, algorithm, limit, summary_writer, repetitions):
    """Funkcja zapisuje wyniki i czas wykonania dla każdej instancji do osobnych plików."""
    sorted_data = [result[:-1] for result in results]
    times = [result[-1] for result in results]

    sorted_output_file_name = output_file_name + '_sorted.csv'
    with open(sorted_output_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Algorithm: {algorithm} file name: {intput_file_name}'])
        writer.writerows(sorted_data)

    time_output_file_name = output_file_name + '_time.csv'
    with open(time_output_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Algorithm: {algorithm} file name: {intput_file_name}'])
        for time in times:
            writer.writerow([time])

    time_elapsed_output_file_name = output_file_name + '_time_elapsed.txt'
    with open(time_elapsed_output_file_name, 'w') as txtfile:
        avg_time = time_elapsed / repetitions
        txtfile.write(
            f'Time: {time_elapsed} (s), Average Time: {avg_time} (s) for algorithm: {algorithm} file name: {intput_file_name} limit: {limit}')
        summary_writer.writerow([algorithm, intput_file_name, limit, avg_time])


def run_algorithm(algorithm_name, data, repetitions, total_tasks):
    """Funkcja wykonuje badany algorytm i zwraca wyniki."""
    results = []
    completed_tasks = 0
    for i in range(repetitions):
        start_time = time.time()
        if algorithm_name == 'bubble_sort':
            sorted_data = bubble_sort(data)
        elif algorithm_name == 'comb_sort':
            sorted_data = comb_sort(data)
        elif algorithm_name == 'radix_sort':
            sorted_data = radix_sort(data)
        elif algorithm_name == 'merge_sort_multithreaded':
            sorted_data = merge_sort_threaded(data)
        else:
            raise ValueError("Nieobsługiwany algorytm.")
        time_elapsed = time.time() - start_time
        results.append(sorted_data + [time_elapsed])

        completed_tasks += 1
        print_progress_bar(completed_tasks, total_tasks, prefix=f'Processing {algorithm_name}', suffix='Complete', length=50)
        time.sleep(0.1)

    return results



def bubble_sort(data):
    """Funkcja implementuje algorytm sortowania bąbelkowego."""
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data


def comb_sort(data):
    """Funkcja implementuje algorytm sortowania grzebieniowego."""
    n = len(data)
    gap = n
    shrink = 1.3
    sorted_data = False

    while not sorted_data:
        gap = int(gap / shrink)
        if gap > 1:
            sorted_data = False
        else:
            gap = 1
            sorted_data = True

        i = 0
        while i + gap < n:
            if data[i] > data[i + gap]:
                data[i], data[i + gap] = data[i + gap], data[i]
                sorted_data = False
            i += 1

    return data


def counting_sort(arr, exp):
    n = len(arr)

    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    result = [0] * n

    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        result[count[index] - 1] = arr[i]
        count[index] -= 1

    return result


def radix_sort(arr):
    max_val = max(arr)

    exp = 1
    while max_val // exp > 0:
        arr = counting_sort(arr, exp)
        exp *= 10

    return arr

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    input_file_names = config.get('data', 'input_files').split(',')
    output_file_names = config.get('data', 'output_files').split(',')
    algorithm_name = config.get('algorithm', 'name').split(',')
    repetitions = int(config.get('experiment', 'repetitions'))
    numbers_to_read = list(map(int, config.get('limits', 'numbers_to_read').split(',')))

    total_tasks = repetitions

    with open('summary.csv', 'w', newline='') as summary_file:
        summary_writer = csv.writer(summary_file)
        summary_writer.writerow(['Algorithm', 'File Name', 'Limit', 'Average Time'])

        for i in range(len(input_file_names)):
            data = read_data_file(input_file_names[i], numbers_to_read[i])

            for algo in algorithm_name:
                total_time_elapsed = 0
                results = run_algorithm(algo, data, repetitions, total_tasks)

                total_time_elapsed = sum([result[-1] for result in results])
                save_results(results, total_time_elapsed, output_file_names[i], input_file_names[i], algo, numbers_to_read[i], summary_writer, repetitions)

if __name__ == '__main__':
    main()
