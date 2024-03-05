#include <cs50.h>
#include <stdio.h>

int main(void)
// TODO: Prompt for start size
{
    int n;
    do
    {
        n = get_int("Initial Size: ");
    }
    while (n < 9);
    // TODO: Prompt for end size
    int j;
    do
    {
        j = get_int("Final Size: ");
    }
    while (j < n);
// TODO: Calculate number of years until we reach threshold
    int c = 0;
    if (n == j)
    {
        printf("Years: 0\n");
        return 0;
    }
    else
        do
        {
            n = n + (n / 3) - (n / 4);
            c += 1;
        }
        while (n < j);
    // TODO: Print number of years
    {
        printf("Years: %i\n", c);
    }
}
