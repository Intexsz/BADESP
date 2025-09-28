#include <iostream>
#include <cstdlib>   // rand, srand
#include <ctime>     // time

int main() {
    std::srand(std::time(0)); // inicializa o gerador de números aleatórios

    int numeros[5];
    std::cout << "Números gerados: ";
    for (int i = 0; i < 5; ++i) {
        numeros[i] = std::rand() % 100; // número aleatório entre 0 e 99
        std::cout << numeros[i] << " ";
    }
    std::cout << std::endl;

    int maior = numeros[0];
    for (int i = 1; i < 5; ++i) {
        if (numeros[i] > maior) {
            maior = numeros[i];
        }
    }

    std::cout << "O maior número é: " << maior << std::endl;

    return 0;
}
