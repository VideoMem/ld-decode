/************************************************************************

    palchromadecoderconfigdialog.cpp

    ld-analyse - TBC output analysis
    Copyright (C) 2019 Simon Inns

    This file is part of ld-decode-tools.

    ld-analyse is free software: you can redistribute it and/or
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

#include "palchromadecoderconfigdialog.h"
#include "ui_palchromadecoderconfigdialog.h"

PalChromaDecoderConfigDialog::PalChromaDecoderConfigDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::PalChromaDecoderConfigDialog)
{
    ui->setupUi(this);
    setWindowFlags(Qt::Window);

    // Set default configuration
    palChromaDecoderConfig.blackAndWhite = false;
    palChromaDecoderConfig.useTransformFilter = true;
    palChromaDecoderConfig.transformThreshold = 0.4;

    ui->thresholdHorizontalSlider->setMinimum(0);
    ui->thresholdHorizontalSlider->setMaximum(100);

    // Update the dialogue
    updateDialog();
}

PalChromaDecoderConfigDialog::~PalChromaDecoderConfigDialog()
{
    delete ui;
}

void PalChromaDecoderConfigDialog::setConfiguration(PalChromaDecoderConfigDialog::PalChromaDecoderConfig _palChromaDecoderConfig)
{
    if (_palChromaDecoderConfig.transformThreshold < 0.00) _palChromaDecoderConfig.transformThreshold = 0.00;
    if (_palChromaDecoderConfig.transformThreshold > 1.00) _palChromaDecoderConfig.transformThreshold = 1.00;

    palChromaDecoderConfig = _palChromaDecoderConfig;
    updateDialog();
    emit palChromaDecoderConfigChanged();
}

PalChromaDecoderConfigDialog::PalChromaDecoderConfig PalChromaDecoderConfigDialog::getConfiguration()
{
    return palChromaDecoderConfig;
}

void PalChromaDecoderConfigDialog::updateDialog()
{
    if (palChromaDecoderConfig.blackAndWhite) ui->blackAndWhiteCheckBox->setChecked(true);
    else ui->blackAndWhiteCheckBox->setChecked(false);

    if (palChromaDecoderConfig.useTransformFilter) {
        ui->twoDeeTransformCheckBox->setChecked(true);
        ui->thresholdHorizontalSlider->setEnabled(true);
        ui->thresholdValueLabel->setEnabled(true);
    } else {
        ui->twoDeeTransformCheckBox->setChecked(false);
        ui->thresholdHorizontalSlider->setEnabled(false);
        ui->thresholdValueLabel->setEnabled(false);
    }

    ui->thresholdHorizontalSlider->setValue(static_cast<qint32>(palChromaDecoderConfig.transformThreshold * 100));
    ui->thresholdValueLabel->setText(QString::number(palChromaDecoderConfig.transformThreshold, 'f', 2));
}

// Methods to handle changes to the dialogue

void PalChromaDecoderConfigDialog::on_blackAndWhiteCheckBox_clicked()
{
    if (ui->blackAndWhiteCheckBox->isChecked()) palChromaDecoderConfig.blackAndWhite = true;
    else palChromaDecoderConfig.blackAndWhite = false;
    emit palChromaDecoderConfigChanged();
}

void PalChromaDecoderConfigDialog::on_twoDeeTransformCheckBox_clicked()
{
    if (ui->twoDeeTransformCheckBox->isChecked()) palChromaDecoderConfig.useTransformFilter = true;
    else palChromaDecoderConfig.useTransformFilter = false;
    updateDialog();
    emit palChromaDecoderConfigChanged();
}

void PalChromaDecoderConfigDialog::on_thresholdHorizontalSlider_valueChanged(int value)
{
    palChromaDecoderConfig.transformThreshold = static_cast<double>(value) / 100;
    ui->thresholdValueLabel->setText(QString::number(palChromaDecoderConfig.transformThreshold, 'f', 2));
    emit palChromaDecoderConfigChanged();
}