#include "core.h"
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <chrono>
#include <iostream>


using namespace std;


word_t** load_pbm(FILE* file, size_t* n_elements) {
    char header[2];
    fread(header, 1, 2, file);
    assert(header[0] == 'P' && header[1] == '4');

    int dimension, n;
    fscanf(file, "%d %d", &dimension, &n);
    assert(dimension == BITS);

    *n_elements = n;
    word_t **hvs = (word_t **)malloc(n*sizeof(word_t *));

    for (int i = 0; i < n; ++i) {
        hvs[i] = bhv::empty();
        fread(hvs[i], 1, BYTES, file);
    }

    return hvs;
}


void save_pbm(FILE* file, word_t** data, size_t n_elements) {
    fwrite("P4", 1, 2, file);

    fprintf(file, "\n%d %zu\n", BITS, n_elements);

    for (size_t i = 0; i < n_elements; ++i)
        fwrite(data[i], 1, BYTES, file);
}

int main() {
    FILE* file = fopen("gol1024.pbm", "rb");
    if (file == nullptr) {
        perror("Failed to open file");
        return 1;
    }

    size_t n;
    word_t** hvs = load_pbm(file, &n);
    assert(n == 1024);

    fclose(file);

    auto t0 = chrono::high_resolution_clock::now();

    for (size_t i = 0; i < n; ++i)
        bhv::rehash_into(hvs[i], hvs[i]);

    auto t1 = chrono::high_resolution_clock::now();

    cout << chrono::duration_cast<chrono::nanoseconds>(t1 - t0).count() << endl;

    FILE* ofile = fopen("hash_gol1024.pbm", "wb");

    save_pbm(ofile, hvs, n);

    fclose(ofile);

    for (size_t i = 0; i < n; ++i)
        free(hvs[i]);

    return 0;
}
