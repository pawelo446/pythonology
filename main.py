import configparser
import csv
import datetime
import os
import time
from typing import List, Tuple

import networkx as nx
from networkx import is_strongly_connected


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
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(edges)
    edge_list = [(u, v, weight["weight"]) for u, v, weight in graph.edges(data=True)]
    return edge_list


def run_algorithm(algorithm_name, data, repetitions, max_iterations, source) -> List[List[int]]:
    results = []
    if algorithm_name == 'dijkstra':
        for _ in range(repetitions):
            start_time = time.time()
            distances, paths = dijkstra_with_path(data, source)
            time_elapsed = time.time() - start_time
            results.append((distances, paths, time_elapsed))
    else:
        raise ValueError("Nieobsługiwany algorytm.")
    return results


def dijkstra_with_path(graph: nx.DiGraph, source: int) -> Tuple[List[int], List[List[int]]]:
    visited = set()
    distances = {node: float('inf') for node in graph.nodes}
    distances[source] = source
    paths = {node: [] for node in graph.nodes}
    paths[source] = [source]

    while len(visited) < len(graph.nodes):
        min_node = None
        for node in graph.nodes:
            if node not in visited:
                if min_node is None:
                    min_node = node
                elif distances[node] < distances[min_node]:
                    min_node = node

        visited.add(min_node)

        for neighbor, weight in graph[min_node].items():
            new_distance = distances[min_node] + weight['weight']
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                paths[neighbor] = paths[min_node] + [neighbor]

    return distances, paths


def remove_edges(data: List[Tuple[int, int, int]], removal_percentage: int) -> List[Tuple[int, int, int]]:
    if removal_percentage == 0:
        return data
    edges = [(i, j, weight) for i, j, weight in data]
    edges.sort(key=lambda x: x[2], reverse=True)

    for n_removed in range(removal_percentage * len(data) // 100, len(data)):
        removed_edges = edges[:len(edges) - n_removed]

        # Create a new graph with the removed edges and ensure that it's connected
        new_graph = nx.DiGraph()
        new_graph.add_weighted_edges_from(removed_edges)

        if is_strongly_connected(new_graph):
            break
    return removed_edges


def save_results(results, time_elapsed, output_file_name, input_file_name, algorithm, step, summary_writer,
                 repetitions, output_directory, edge_removal_percentages):
    """Funkcja zapisuje wyniki i czas wykonania dla każdej instancji do osobnych plików."""
    sorted_data = [result[:-1] for result in results]
    times = [result[-1] for result in results]

    paths_output_file_name = os.path.join(output_directory, output_file_name + '_paths.csv')
    with open(paths_output_file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Algorithm: {algorithm} file name: {input_file_name}'])
        for result in results:
            paths = result[1]
            for node, path in paths.items():
                writer.writerow([node, path])
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
            f'Time: {time_elapsed} (s), Average Time: {avg_time} (s) for algorithm: {algorithm} file name: {input_file_name} step size: {step} edge removal percentages: {edge_removal_percentages}')
        summary_writer.writerow([algorithm, input_file_name, step, avg_time])
        print(f'Time: {time_elapsed} (s), Average Time: {avg_time} (s) for algorithm: {algorithm} file name: {input_file_name} step size: {step} edge removal percentages: {edge_removal_percentages}')


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    input_file_names = config.get('data', 'input_files').split(',')
    output_file_names = config.get('data', 'output_files').split(',')
    algorithm_name = config.get('algorithm', 'name').split(',')
    repetitions = int(config.get('experiment', 'repetitions'))
    max_iterations = int(config.get('limits', 'max_iterations'))
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
                    print(f"Przetwarzanie kroku: {step}, Usuwanie krawędzi: {edge_removal_percentage}%")
                    data = read_graph_file(input_file_name)
                    data = remove_edges(data, edge_removal_percentage)  # Dodajemy usuwanie krawędzi

                    # Convert the removed edges to a NetworkX graph
                    graph = nx.DiGraph()
                    graph.add_weighted_edges_from(data)
                    # if nx.is_strongly_connected(graph):
                    input_data = data
                    # else:
                    #     print("Pominięcie przypadku: Graf nie jest spójny")
                    #     continue
                    
                    source = 1  # Wybierz węzeł startowy (np. 0)
                    print("Uruchomienie algorytmu...")
                    results = run_algorithm(algorithm, graph, repetitions, max_iterations, source)
                    print(f"results: {results}")
                    time_elapsed = sum(result[-1] for result in results)
                    output_file_suffix = f"__step_{step}_removal_{edge_removal_percentage}"
                    save_results(results, time_elapsed, output_file_name + output_file_suffix, input_file_name,
                                 algorithm, step, summary_writer, repetitions, output_directory,
                                 edge_removal_percentages)


if __name__ == '__main__':
    main()
