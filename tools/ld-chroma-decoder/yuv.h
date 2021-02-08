/************************************************************************

    yuv.h

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

#ifndef YUV_H
#define YUV_H

#include <QCoreApplication>
#include <QDebug>

#include "yiq.h"

// BT.601
#define Kb (1 - 0.114)
#define Kr (1 - 0.299)

// Poynton, "Digital Video and HDTV" first edition, Eq 28.1
#define kB 0.49211104112248356308804691718185
#define kR 0.877283221458919247158029475165

#define SIN33 0.54463903501502708222408369208157
#define COS33 0.83867056794542402963759094180455

class YUV
{
public:
    // whiteIreLevel: 100 IRE 16-bit level
    // blackIreLevel: 0 or 7.5 IRE 16-bit level
    // whitePoint75: false = using 100% white point, true = 75%
    // chromaGain: gain applied to I/Q channels
    YUV(double whiteIreLevel, double blackIreLevel, bool whitePoint75, double chromaGain);

    void convertLine(const YIQ *begin, const YIQ *end, quint16 *outY, quint16 *outU, quint16 *outV);

private:
    double whiteIreLevel;
    double blackIreLevel;
    bool whitePoint75;
    double chromaGain;
};

#endif // YUV_H
