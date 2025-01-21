#include <iostream>
#include <omp.h>
#include <random>
#include <climits>
#include <cstring>
#include <cstdlib>
#include <chrono>

#pragma region Defaults

#define N_THREADS 10 
#define CHUNK_SIZE 100
#define N_ITEMS 100000
#define MAX_OUTPUT_ROWS 10

#pragma endregion

#pragma region CLI argument parsing

struct Arguments {
    int n_threads;
    int chunk_size;
    int n_items;
    int max_output_rows;
};

Arguments parse_arguments(int argc, char* argv[]) {
    int n_threads = N_THREADS;
    int chunk_size = CHUNK_SIZE;
    int n_items = N_ITEMS;
    int max_output_rows = MAX_OUTPUT_ROWS;

    for (int i = 1; i < argc; i++) {
        if (std::strcmp(argv[i], "--threads") == 0 && i + 1 < argc) {
            n_threads = std::atoi(argv[++i]);
        }
        else if (std::strcmp(argv[i], "--chunk_size") == 0 && i + 1 < argc) {
            chunk_size = std::atoi(argv[++i]);
        }
        else if (std::strcmp(argv[i], "--items") == 0 && i + 1 < argc) {
            n_items = std::atoi(argv[++i]);
        }
        else if (std::strcmp(argv[i], "--max_output_rows") == 00 && i + 1 < argc) {
            max_output_rows = std::atoi(argv[++i]);
        }
    }

    return {
        n_threads,
        chunk_size,
        n_items,
        max_output_rows
    };
}

#pragma endregion

#pragma region Number Generators

// https://en.wikipedia.org/wiki/Triangular_number
int* triangular_numbers(int* arr, int n) {
    for (int i = 0; i < n; i++) {
        arr[i] = (i * (i + 1)) / 2;
    }

    return arr;
}

int* random_numbers(int* arr, int n) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 100000);

    for (int i = 0; i < n; i++) {
        arr[i] = dis(gen);
    }

    return arr;
}

#pragma endregion


void output_results(int max_output_rows, int* a, int* b, int* c, int n_items) {
    if (max_output_rows == 0) {
        return;
    }

    if (n_items <= max_output_rows) {
        for (int i = 0; i < n_items; i++) {
            std::cout << a[i] << " + " << b[i] << " = " << c[i] << std::endl;
        }

        return;
    }

    for (int i = 0; i < max_output_rows / 2; i++) {
        std::cout << a[i] << " + " << b[i] << " = " << c[i] << std::endl;
    }

    std::cout << "." << std::endl << "." << std::endl << "." << std::endl;

    for (int i = n_items - (max_output_rows / 2); i < n_items; i++) {

        std::cout << a[i] << " + " << b[i] << " = " << c[i] << std::endl;
    }
}


void parallel_array_sum(int* a, int* b, int* c, int n_items, int chunk_size) {
    int i;
    #pragma omp parallel for shared(a, b, c) private(i) schedule(static, chunk_size)
    for (i = 0; i < n_items; i++) {
        c[i] = a[i] + b[i];
    }
}

int main(int argc, char* argv[])
{
    Arguments args = parse_arguments(argc, argv);

    std::cout << "Performing parallel array sum with:\n"
        << "Threads: " << args.n_threads << std::endl
        << "Items: " << args.n_items << std::endl
        << "Chunk size: " << args.chunk_size << std::endl
        << "Output rows: " << args.max_output_rows << std::endl
        << std::endl;

    int* a = new int[args.n_items];
    int* b = new int[args.n_items];
    int* c = new int[args.n_items];

    a = triangular_numbers(a, args.n_items);
    b = random_numbers(b, args.n_items);

#ifdef _OPENMP
    std::cout << "OpenMP is enabled" << std::endl;
    omp_set_num_threads(args.n_threads);
#endif // _OPENMP

    auto start = std::chrono::high_resolution_clock::now();
    parallel_array_sum(a, b, c, args.n_items, args.chunk_size);
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Summed arrays in: " << elapsed.count() << " seconds." << std::endl;

    output_results(args.max_output_rows, a, b, c, args.n_items);

    delete[] a;
    delete[] b;
    delete[] c;

    return 0;
}


