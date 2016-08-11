#include <stdio.h>
#include <math.h>
#include "unify_definition.h"

float getDist(const float a[DIMENTION], const float b[DIMENTION]) {
    float delta = 0;
    float d;
    int i;

    for (i = 0; i < DIMENTION; i++) {
        d = a[i] - b[i];
        delta += d * d;
    }
    return sqrt(delta);
}

void copyPoint(float source[DIMENTION], float dest[DIMENTION]) {
    int i;
    for (i = 0; i < DIMENTION; i++) {
        dest[i] = source[i];
    }    
}

void unifyStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], float newStroke[SEGMENTATION][DIMENTION], int start) {
    float strokeLengths[STROKE_MAX_LENGTH];
    float step;
    int i, j;
    int newStrokeId = 1;
    float nextLength;
    float * p1;
    float * p2;
    float delta;
    float coeff;

    strokeLengths[start] = 0;

    for (i = start + 1; i < STROKE_MAX_LENGTH; i++) {
        strokeLengths[i] = strokeLengths[i - 1] + getDist(stroke[i - 1], stroke[i]);       
    }

    step = strokeLengths[STROKE_MAX_LENGTH - 1] / (SEGMENTATION - 1);

    copyPoint(stroke[start], newStroke[0]);
    copyPoint(stroke[STROKE_MAX_LENGTH - 1], newStroke[SEGMENTATION - 1]);

    nextLength = step;

    for (i = start + 1; i < STROKE_MAX_LENGTH; i++) {
        while (strokeLengths[i] > nextLength) {
            p1 = stroke[i - 1];
            p2 = stroke[i];
            delta = strokeLengths[i] - strokeLengths[i - 1];
            coeff = delta == 0 ? 0 : (1 - ((strokeLengths[i] - nextLength) / delta));
            for (j = 0; j < DIMENTION; j++) {
                newStroke[newStrokeId][j] = p1[j] + (p2[j] - p1[j]) * coeff;
            }
            newStrokeId += 1;
            nextLength += step;
        }
    } 

}

float checkStroke(float stroke[SEGMENTATION][DIMENTION], const float description[SEGMENTATION][DIMENTION + 1]) {
    float errors[SEGMENTATION];
    float mean = 0;
    float result = 0;
    float radius;
    float d;
    int i;

    for (i = 0; i < SEGMENTATION; i++) {
        radius = getDist(stroke[i], description[i]) - description[i][3];
        radius = radius < 0 ? 0 : radius;
        errors[i] = radius;
        mean += radius;
    }

    mean /= SEGMENTATION;

    for (i = 0; i < SEGMENTATION; i++) {
        d = errors[i] - mean;
        result += d * d;
    }
    return sqrt(result / SEGMENTATION);
}

int getStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], int length, unsigned long access) {
    float unifiedStroke[SEGMENTATION][DIMENTION];
    unifyStroke(stroke, unifiedStroke, length);
    int i;
    float error;
    float min_error = MAX_ERROR;
    int strokeId = -1;
    for (i = 0; i < STROKES_COUNT; i++) {
        error = checkStroke(unifiedStroke, STROKES[i]);
        if (error < min_error) {
            strokeId = i;
            min_error = error;
        }
    }
    return strokeId;
}
