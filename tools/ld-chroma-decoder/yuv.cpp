/************************************************************************

    yuv.cpp

    ld-chroma-decoder - Colourisation filter for ld-decode
    Copyright (C) 2018 Chad Page
    Copyright (C) 2018-2019 Simon Inns

    This file is part of ld-decode-tools.

    ld-chroma-decoder is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

************************************************************************/

#include "yuv.h"


YUV::YUV(double _whiteIreLevel, double _blackIreLevel, bool _whitePoint75, double _chromaGain)
    : whiteIreLevel(_whiteIreLevel), blackIreLevel(_blackIreLevel), whitePoint75(_whitePoint75),
      chromaGain(_chromaGain)
{
}

void YUV::convertLine(const YIQ *begin, const YIQ *end, quint16 *outY, quint16 *outU, quint16 *outV)
{
    // Factors to scale Y according to the black to white interval
    // (i.e. make the black level 0 and the white level 65535)
    double yBlackLevel = blackIreLevel;

    double yScale = 219*257 / (whiteIreLevel - blackIreLevel);
    // Compute I & Q scaling factor.
    // This is the same as for Y, i.e. when 7.5% setup is in use the chroma
    // scale is reduced proportionately.
    //const double iqScale = yScale * chromaGain;

    if (whitePoint75) {
        // NTSC uses a 75% white point; so here we scale the result by
        // 25% (making 100 IRE 25% over the maximum allowed white point).
        // This doesn't affect the chroma scaling.
        yScale *= 125.0 / 100.0;
    }

    const double iqScale = chromaGain * 229*255 / (whiteIreLevel - blackIreLevel) / 65535.0;
    const double cbScale = 112*256 / (Kb * kB); // Poynton, Eq 25.5 & 28.1
    const double crScale = 112*256 / (Kr * kR);
    for (const YIQ *yiq = begin; yiq < end; yiq++) {
        double y = yiq->y;
        double i = yiq->i;
        double q = yiq->q;
        // Scale the Y to 0-65535 where 16*256 = blackIreLevel and 235*256 = whiteIreLevel
        y = (y - yBlackLevel) * yScale + 16*256;
        y = qBound(0.0, y, 65535.0);
        // Scale the I & Q components to [0,1]
        i *= iqScale;
        q *= iqScale;

        // Rotate 33 degrees to U & V
        double U = (-SIN33 * i + COS33 * q);
        double V = ( COS33 * i + SIN33 * q);

        // Scale and offset to create CbCr
        double Cb = U * cbScale + 128*256;
        double Cr = V * crScale + 128*256;

        Cb = qBound(0.0, Cb, 65535.0);
        Cr = qBound(0.0, Cr, 65535.0);

        // Place the 16-bit YCbCr values in the output array
        *outY++ = static_cast<quint16>(y);
        *outU++ = static_cast<quint16>(Cb);
        *outV++ = static_cast<quint16>(Cr);
    }
}
