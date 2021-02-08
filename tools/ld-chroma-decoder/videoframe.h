/************************************************************************

    videoframe.h

    ld-chroma-decoder - Colourisation filter for ld-decode
    Copyright (C) 2020 Adam Sampson

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

#ifndef VIDEOFRAME_H
#define VIDEOFRAME_H

#include <QtGlobal>
#include <QVector>

// A decoded frame, containing triples of (Y, U, V) samples
// using YUVFrame = struct{ QVector<quint16>, QVector<quint16>, QVector<quint16> };
typedef struct
{
    QVector<quint16> RGB;
    QVector<quint16> y;
    QVector<quint16> u;
    QVector<quint16> v;
} videoFrame;

#endif // VIDEOFRAME_H
