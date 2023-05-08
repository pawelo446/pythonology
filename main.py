import configparser
import csv
import os
import time
from typing import List
import datetime
import networkx as nx
from networkx import is_connected
import random
from typing import List, Tuple


def flatMap(l):
    return [item for sublist in l for item in sublist]


def krotki_read_graph_file(file_name):
    """Funkcja odczytuje dane z pliku i zwraca je w odpowiednim formacie."""
    extension = file_name.split('.')[-1]
    if extension == 'csv':
        with open(file_name, newline='') as csvfile:
            data = [(int(row[0]), int(row[1]), int(row[2])) for row in csv.reader(csvfile)]
            print(f"Dane wczytane z pliku: {data}")
    elif extension == 'txt':
        with open(file_name) as txtfile:
            data = [(int(row.split(',')[0]), int(row.split(',')[1]), int(row.split(',')[2])) for row in txtfile]
    else:
        raise ValueError("Nieobsługiwany format pliku wejściowego.")
    print(f"Pobrano graf z pliku {file_name}")
    # Przekształcanie listy krawędzi w obiekt grafu
    graph = nx.Graph()
    graph.add_weighted_edges_from(data)
    edge_list = [(u, v, weight["weight"]) for u, v, weight in graph.edges(data=True)]
    return edge_list


def read_graph_file(file_name):
    extension = file_name.split('.')[-1]
    if extension == 'csv':
        with open(file_name, newline='') as csvfile:
            data = [list(map(int, row)) for row in csv.reader(csvfile)]
            print(f"Dane wczytane z pliku: {data}")
    elif extension == 'txt':
        with open(file_name) as txtfile:
            data = [list(map(int, row.split(','))) for row in txtfile]
    else:
        raise ValueError("Nieobsługiwany format pliku wejściowego.")

    print(f"Pobrano graf z pliku {file_name}")
    # Przekształcanie macierzy sąsiedztwa w listę krawędzi z wagami
    n = len(data)
    edges = [(i, j, data[i][j]) for i in range(n) for j in range(i + 1, n) if data[i][j] > 0]

    # Przekształcanie listy krawędzi w obiekt grafu
    graph = nx.Graph()
    graph.add_weighted_edges_from(edges)
    edge_list = [(u, v, weight["weight"]) for u, v, weight in graph.edges(data=True)]
    return edge_list


def run_algorithm(algorithm_name, data, repetitions) -> List[List[int]]:
    results = []
    if algorithm_name == 'boruvka':
        for i in range(repetitions):
            start_time = time.time()
            mst = boruvka_mst(data)
            time_elapsed = time.time() - start_time
            results.append(mst + [time_elapsed])
    else:
        raise ValueError("Nieobsługiwany algorytm.")
    return results


def boruvka_mst(edges) -> List[List[int]]:
    n = max([max(edge[0], edge[1]) for edge in edges]) + 1
    graph = nx.Graph()
    graph.add_weighted_edges_from(edges)
    mst = nx.Graph()

    while mst.number_of_edges() < n - 1:
        cheapest_edges = [-1] * n

        for u, v, weight in graph.edges.data("weight"):
            if mst.number_of_edges() == 0 or not nx.has_path(mst, u, v):
                if cheapest_edges[u] == -1 or cheapest_edges[u][2] > weight:
                    cheapest_edges[u] = (u, v, weight)
                if cheapest_edges[v] == -1 or cheapest_edges[v][2] > weight:
                    cheapest_edges[v] = (v, u, weight)

        for edge in cheapest_edges:
            if edge != -1:
                u, v, weight = edge
                if not mst.has_edge(u, v):
                    mst.add_edge(u, v, weight=weight)
    return [(u, v, weight) for u, v, weight in mst.edges.data("weight")]


def remove_edges(data: List[Tuple[int, int, int]], removal_percentage: int) -> List[Tuple[int, int, int]]:
    if removal_percentage == 0:
        return data
    n = int(len(data) * (1 - removal_percentage / 100))
    edges = [(i, j, weight) for i, j, weight in data]
    edges.sort(key=lambda x: x[2])
    removed_edges = edges[:len(edges) - n]
    return removed_edges


def save_results(results, time_elapsed, output_file_name, input_file_name, algorithm, step, summary_writer,
                 repetitions, output_directory):
    """Funkcja zapisuje wyniki i czas wykonania dla każdej instancji do osobnych plików."""
    sorted_data = [result[:-1] for result in results]
    times = [result[-1] for result in results]

    sorted_output_file_name = os.path.join(output_directory, output_file_name + '_mst.csv')
    with open(sorted_output_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Algorithm: {algorithm} file name: {input_file_name}'])
        writer.writerows(sorted_data)

    time_output_file_name = os.path.join(output_directory, output_file_name + '_time.csv')
    with open(time_output_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Algorithm: {algorithm} file name: {input_file_name}'])
        for time in times:
            writer.writerow([time])

    time_elapsed_output_file_name = os.path.join(output_directory, output_file_name + '_time_elapsed.txt')
    with open(time_elapsed_output_file_name, 'w') as txtfile:
        avg_time = time_elapsed / repetitions
        txtfile.write(
            f'Time: {time_elapsed} (s), Average Time: {avg_time} (s) for algorithm: {algorithm} file name: {input_file_name} step: {step}')
        summary_writer.writerow([algorithm, input_file_name, step, avg_time])
        print(f'Time: {time_elapsed} (s), Average Time: {avg_time} (s) for algorithm: {algorithm} file name: {input_file_name} step: {step}')

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    input_file_names = config.get('data', 'input_files').split(',')
    output_file_names = config.get('data', 'output_files').split(',')
    algorithm_name = config.get('algorithm', 'name').split(',')
    repetitions = int(config.get('experiment', 'repetitions'))
    step_sizes = list(map(int, config.get('limits', 'step_sizes').split(',')))
    edge_removal_percentages = list(map(int, config.get('limits', 'edge_removal_percentages').split(',')))

    # Create a new directory with the current date and time
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_directory = f'output_{now}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(f'{output_directory}/summary.csv', 'w', newline='') as summary_file:
        summary_writer = csv.writer(summary_file)
        summary_writer.writerow(['Algorithm', 'File Name', 'Step', 'Average Time'])

        for input_file_name, algorithm, output_file_name in zip(input_file_names, algorithm_name, output_file_names):
            for step in step_sizes:
                for edge_removal_percentage in edge_removal_percentages:
                    data = read_graph_file(input_file_name)
                    data = remove_edges(data, edge_removal_percentage)  # Dodajemy usuwanie krawędzi
                    # Convert the removed edges to a NetworkX graph
                    graph = nx.Graph()
                    graph.add_weighted_edges_from(data)
                    if is_connected(graph):
                        input_data = data
                    else:
                        continue
                    start_time = time.time()
                    results = run_algorithm(algorithm, input_data, repetitions)
                    print(f"results: {results}")
                    time_elapsed = time.time() - start_time
                    output_file_suffix = f"__step_{step}_removal_{edge_removal_percentage}"
                    save_results(results, time_elapsed, output_file_name + output_file_suffix, input_file_name,
                                 algorithm, step, summary_writer, repetitions, output_directory)


if __name__ == '__main__':
    main()