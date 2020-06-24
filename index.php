<?php

use setasign\Fpdi\Tcpdf\Fpdi;
require_once('vendor/autoload.php');

$pdf = new Fpdi();

$pdf->setPrintHeader(false);
$pdf->setPrintFooter(false);

$pdf->AddPage();
$pdf->setSourceFile('template.pdf');
$tplId = $pdf->importPage(1);
$pdf->useTemplate($tplId, 0, 0, null, null, true);

$pdf->SetFont('helvetica', "", 12);
$pdf->SetTextColor(0, 0, 0);
$pdf->Text(76,32,"Text value 1");

$pdf->Output(__DIR__ . '/php_result.pdf', 'F');