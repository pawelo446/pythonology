import configparser

def build_kmp_table(pattern):
    pattern_length = len(pattern)
    kmp_table = [0] * pattern_length
    j = 0

    for i in range(1, pattern_length):
        if pattern[i] == pattern[j]:
            j += 1
            kmp_table[i] = j
        else:
            if j != 0:
                j = kmp_table[j - 1]
                i -= 1
            else:
                kmp_table[i] = 0
    return kmp_table


def kmp_search(text, pattern):
    kmp_table = build_kmp_table(pattern)
    text_length = len(text)
    pattern_length = len(pattern)
    i = 0
    j = 0
    found_indices = []

    while i < text_length:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == pattern_length:
            found_indices.append(i - j)
            j = kmp_table[j - 1]
        elif i < text_length and pattern[j] != text[i]:
            if j != 0:
                j = kmp_table[j - 1]
            else:
                i += 1
    return found_indices


def read_text_from_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def hash(pattern, prime):
    hashed = 0
    m = len(pattern)
    for i in range(m):
        hashed += ord(pattern[i]) * prime ** (m - i - 1)
    return hashed


def rabin_karp_search(text, pattern):
    prime = 101
    pattern_length = len(pattern)
    text_length = len(text)
    pattern_hash = hash(pattern, prime)
    text_hash = hash(text[:pattern_length], prime)

    found_indices = []

    for i in range(0, text_length - pattern_length + 1):
        if pattern_hash == text_hash and text[i:i + pattern_length] == pattern:
            found_indices.append(i)
        if i < text_length - pattern_length:
            text_hash = (text_hash - ord(text[i]) * prime ** (pattern_length - 1)) * prime + ord(text[i + pattern_length])
    return found_indices


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    text_file_name = config.get('data', 'input_file')
    text = read_text_from_file(text_file_name)

    while True:
        print("Wybierz operację:")
        print("1. Wyszukaj wzorzec za pomocą Rabina-Karpa")
        print("2. Zakończ")

        choice = int(input("Wybór: "))
        if choice in [1, 2]:
            pattern = input("Podaj wzorzec do wyszukania: ")
            if choice == 1:
                found_indices = kmp_search(text, pattern)
            else:
                found_indices = rabin_karp_search(text, pattern)
            print(f"Wzorzec znaleziony {len(found_indices)} razy.")
            print(f"Wzorzec znaleziony na indeksach: {found_indices}")
        elif choice == 3:
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


if __name__ == '__main__':
    main()

