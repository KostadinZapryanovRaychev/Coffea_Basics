#include "helpers.h"

#include <fstream>
#include <cstdio>

void reader(std::string filePath)
{
    std::ifstream file(filePath);

    if (file.is_open())
    {
        printf("File opened successfully: %s\n", filePath.c_str());
        file.close();
    }
    else
    {
        printf("Failed to open file: %s\n", filePath.c_str());
    }
}