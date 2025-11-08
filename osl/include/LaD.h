/*
 *  Copyright 2023 LAIKA. Authored by Mitch J Prater.
 *
 *  Licensed under the Apache License Version 2.0 http://apache.org/licenses/LICENSE-2.0,
 *  or the MIT license http://opensource.org/licenses/MIT, at your option.
 *
 *  This program may not be copied, modified, or distributed except according to those terms.
 */

// The LaSh Displacement struct.
struct LaD_struct
{
    // Displacement layering controls.
    float  Mask;
    float  Thickness;
    float  Accumulation;
    float  TauScale;

    // Displacement data.
    normal Nd; // Displaced surface normal.
    vector DeltaP; // Displacement vector.
    float  Bulk; // Accumulation Bulk.
};

// Default values.
#define LaD_INIT {1.0, 0.0, 0.0, 1.0, N, vector(0.0), 0.0 }
