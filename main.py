import configparser
import csv


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)

    def delete(self, value):
        self.root = self._delete_recursive(self.root, value)

    def _delete_recursive(self, node, value):
        if node is None:
            return node
        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                min_value = self._find_min_value(node.right)
                node.value = min_value
                node.right = self._delete_recursive(node.right, min_value)
        return node

    def _find_min_value(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current.value

    def search(self, value):
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        if node is None or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)

    def print_tree(self):
        def height(root):
            if root is None:
                return 0
            return max(height(root.left), height(root.right)) + 1

        def getcol(h):
            if h == 1:
                return 1
            return getcol(h - 1) + getcol(h - 1) + 1

        def printTree(M, root, col, row, height):
            if root is None:
                return
            M[row][col] = root.value
            printTree(M, root.left, col - pow(2, height - 2), row + 1, height - 1)
            printTree(M, root.right, col + pow(2, height - 2), row + 1, height - 1)

        h = height(self.root)
        col = getcol(h)
        M = [[0 for _ in range(col)] for __ in range(h)]
        printTree(M, self.root, col // 2, 0, h)
        for i in M:
            for j in i:
                if j == 0:
                    print(" ", end=" ")
                else:
                    print(j, end=" ")
            print("")


def read_numbers_from_csv(file_name):
    numbers = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for number in row:
                numbers.append(int(number))
    return numbers


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    csv_file_name = config.get('data', 'input_file')

    numbers = read_numbers_from_csv(csv_file_name)

    bst = BST()

    for number in numbers:
        bst.insert(number)

    while True:
        print("Wybierz operację:")
        print("1. Dodaj wartość")
        print("2. Usuń wartość")
        print("3. Wyszukaj wartość")
        print("4. Wyświetl drzewo")
        print("5. Zakończ")

        choice = int(input("Wybór: "))

        if choice == 1:
            value = int(input("Podaj wartość do dodania: "))
            bst.insert(value)
            print("Wartość dodana.")
        elif choice == 2:
            value = int(input("Podaj wartość do usunięcia: "))
            bst.delete(value)
            print("Wartość usunięta.")
        elif choice == 3:
            value = int(input("Podaj wartość do wyszukania: "))
            if bst.search(value):
                print("Wartość znaleziona.")
            else:
                print("Wartość nie znaleziona.")
        elif choice == 4:
            print("Drzewo:")
            bst.print_tree()
        elif choice == 5:
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


if __name__ == '__main__':
    main()
