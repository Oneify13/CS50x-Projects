#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int total = image[i][j].rgbtBlue + image[i][j].rgbtRed + image[i][j].rgbtGreen;
            //Calculates the average of all the colors in a single pixel.
            int average = round(total / 3.0);

            //Sets the values of each color to the average of all the previous color values in that pixel.
            image[i][j].rgbtBlue = average;
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //Calculates the correct amount of each color.
            int sepiaRed = round(.393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue);
            int sepiaGreen = round(.349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue);
            int sepiaBlue = round(.272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue);

            //Conditionals in case the sepia color values go above 255.
            if (sepiaRed > 255)
            {
                sepiaRed = 255;
            }
            if (sepiaGreen > 255)
            {
                sepiaGreen = 255;
            }
            if (sepiaBlue > 255)
            {
                sepiaBlue = 255;
            }

            image[i][j].rgbtRed = sepiaRed;
            image[i][j].rgbtGreen = sepiaGreen;
            image[i][j].rgbtBlue = sepiaBlue;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];

    //Switches the values of the pixels and stores them in a temporary place holder/
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; (width - j - 1) >= j; j++)
        {
            copy[i][j] = image[i][width - j - 1];
            copy[i][width - j - 1] = image[i][j];
        }




    }

    //Takes the values of copy and transfers them to the actaul pixels.
    for (int a = 0; a < height; a++)
    {
        for (int b = 0; b < width; b++)
        {
            image[a][b] = copy[a][b];
        }
    }
    return;
}
// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    //Variable to copy the rgb values into.
    RGBTRIPLE copy[height][width];

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            double count = 0;
            int totalRed = 0;
            int totalGreen = 0;
            int totalBlue = 0;

            for (int n = -1; n < 2; n++)
            {
                for (int m = -1; m < 2; m++)
                {
                    if (i + n < height && i + n >= 0 && j + m < width && j + m >= 0)
                    {
                        //Calculates total amount of each color and the number of pixels.
                        totalRed += image[i + n][j + m].rgbtRed;
                        totalGreen += image[i + n][j + m].rgbtGreen;
                        totalBlue += image[i + n][j + m].rgbtBlue;
                        count++;
                    }



                    //Determines the average amount of each color in the selected pixels.
                    int averageRed = round(totalRed / count);
                    int averageGreen = round(totalGreen / count);
                    int averageBlue = round(totalBlue / count);

                    //Copies the average values into a variable that will temporarily store them.
                    copy[i][j].rgbtRed = averageRed;
                    copy[i][j].rgbtGreen = averageGreen;
                    copy[i][j].rgbtBlue = averageBlue;
                }
            }
        }

    }

    //Takes the values of copy and transfers them to the actual pixels.
    for (int a = 0; a < height; a++)
    {
        for (int b = 0; b < width; b++)
        {
            image[a][b] = copy[a][b];
        }
    }
}