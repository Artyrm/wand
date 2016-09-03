#ifndef UnifyDefinition_h
#define UnifyDefinition_h

#include "knowledge.h"

float getDist(const float a[DIMENTION], const float b[DIMENTION]);
void unifyStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], float newStroke[SEGMENTATION][DIMENTION], int length);
int getStroke(float stroke[STROKE_MAX_LENGTH][DIMENTION], int length, unsigned long access);
float checkStroke(float stroke[SEGMENTATION][DIMENTION], const float description[SEGMENTATION][DIMENTION]);

#endif
