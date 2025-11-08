/*
 *  Copyright 2022 LAIKA. Authored by Mitch J Prater.
 *
 *  Licensed under the Apache License Version 2.0 http://apache.org/licenses/LICENSE-2.0,
 *  or the MIT license http://opensource.org/licenses/MIT, at your option.
 *
 *  This program may not be copied, modified, or distributed except according to those terms.
 */
#pragma once

//----------------------------------------------------------------------
//  Micropolygon Size
//  How many object space units per micropolygon?
//----------------------------------------------------------------------
float ikaMpSize( point Po )
{
    float  mp_length; // micropolygon edge length in pixels.
    getattribute( "dice:micropolygonlength", mp_length );
    mp_length *= 1000;

    // "raster" = pixels.
    point  Praster0 = transform( "common", "raster", Po );
    point  Praster1 = Praster0 + vector( mp_length, mp_length, 0 );

    point  Pobject0 = transform( "raster", "object", Praster0 );
    point  Pobject1 = transform( "raster", "object", Praster1 );

    // micropolygon Size: object units per micropolygon.
    return (0.001/M_SQRT2) * length( Pobject1 - Pobject0 );
}

float ikaMpSize()
{
    point  Po = P; // un-displaced P.
    getattribute( "builtin", "Po", Po );

    // micropolygon Size: object units per micropolygon.
    return ikaMpSize( Po );
}

//----------------------------------------------------------------------
//  Bump/Displacement Mix
//
//  Produces the highest fidelity surface variation representation
//  for a given pattern's Size.
//  When a pattern's feature size is too small to be accurately
//  represented by the geometry's micropolygons, its surface
//  variation must instead be represented by a bumped shading normal.
//
//  patternSize = object units / pattern feature.
//  Ratio adjusts the bump/disp ratio:
//      Ratio < 1 more bump; 1 < Ratio more disp;
//----------------------------------------------------------------------
float ikaBumpDispMix( float patternSize, float mpSize, float Ratio )
{
    // patternSize / mpSize => micropolygons per pattern feature.
    // Bump to displacement transition begins at 4 mp's per pattern
    // feature and transitions to full displacement at 8.25
    return  smooth_linearstep( 4.25, 8.0, (patternSize/mpSize)*Ratio, 0.25 );
}

//----------------------------------------------------------------------
//  Prater normal forward projection method with no branching.
//  Ensures the normal is facing the view vector.
//  Note: neither input needs to be normalized,
//  nor is the result normalized.
//----------------------------------------------------------------------
normal ikaProjectForward( normal Norm, vector View )
{
    // If the object's surface faces the view direction...
    int frontNg = dot( Ng, View ) >= 0.0;
    
    // ...and the normal is facing away from the view direction...
    vector Vn = normalize( View );
    float  NdotVn = dot( Norm, Vn );
    int  backN = NdotVn <= 0.0;
    
    // ...project the normal forward so it's perpendicular to the
    // view + 1% more to avoid numerical dithering at the silhouette.
    int  projectForward = frontNg && backN;
    normal forwardN = select( Norm, Norm - 1.01*NdotVn*Vn, projectForward );
    
    // Return the (un-normalized) forward projected normal.
    return forwardN;
}

normal ikaProjectForward( normal Norm )
{
    return ikaProjectForward( Norm, -I );
}

//----------------------------------------------------------------------
//  Mikkelsen, M. 2020
//  Surface Gradient–Based Bump Mapping Framework
//  Journal of Computer Graphics Techniques, Vol. 9, No. 3
//  https://jcgt.org/published/0009/03/04/
//  Note that neither input needs to be normalized.
//----------------------------------------------------------------------
vector ikaSurfaceGradient( vector Nb, vector Nr )
{
    // Compute the surface gradient from the normal.
    float  k = dot( Nr, Nb );
    vector surfGrad = ( k*Nr - Nb )/max( 1.0e-6, abs(k) );

    // Return the surface gradient vector.
    return surfGrad;
}

vector ikaSurfaceGradient( vector Nb )
{
    return ikaSurfaceGradient( Nb, Ng );
}

//----------------------------------------------------------------------
//  Surface Gradient to Normal.
//----------------------------------------------------------------------
normal ikaSurfaceGradientToNormal( vector SurfaceGradient, float Gain )
{
    return normalize( N - SurfaceGradient*Gain );
}

normal ikaSurfaceGradientToNormal( vector SurfaceGradient )
{
    return normalize( N - SurfaceGradient );
}
