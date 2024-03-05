#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    typedef uint8_t BYTE;

    if (argc != 2)
    {
        printf("Usage: ./recover IMAGE\n");
        return 1;
    }



    //Opens the card.raw file
    FILE *raw_file = fopen(argv[1], "r");
    if (raw_file == NULL)
    {
        printf("No file found.\n");
        return 2;
    }

    BYTE buffer[512];
    //Keeps track of the amount of jpegs.
    int jpegs = 0;

    char file_name [8];

    //Creates the file for the jpegs to be written onto.
    FILE *new_file = NULL;

    while (fread(buffer, sizeof(BYTE) * 512, 1, raw_file) == 1)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            //Closes previously opened file if there is a new jpeg.
            if (jpegs > 0)
            {
                fclose(new_file);
            }

            //Creates the jpeg.
            sprintf(file_name, "%03i.jpg", jpegs);
            new_file = fopen(file_name, "w");
            jpegs++;
            fwrite(buffer, sizeof(BYTE) * 512, 1, new_file);
        }
        //If moved onto next block and not start of new jpeg keep writing.
        else if (jpegs > 0)
        {
            fwrite(buffer, sizeof(BYTE) * 512, 1, new_file);
        }

    }
    fclose(raw_file);
    fclose(new_file);
}